"""drafts_adapter.py · Phase 10.3 · persona 视角 C2 草稿池薄适配脚本.

与 ``publish_adapter.py`` / ``rewrite_adapter.py`` / ``regenerate_adapter.py`` 同层：
本文件是唯一 import ``scripts.compose`` 的「草稿池扇出」入口，耦合收敛在这一处。
``serve.py``（10.4）通过 subprocess 调用本模块，不需要自己拼装 news/candidate/judge。

职责边界（ADR-0017 D3/D5/D6）：
- **全量扇出**（默认动作）：读 ``candidate.triggered_by``（命中该片的 persona 全集，
  无数量上限），对每个 persona 各注入其**蒸馏视角**跑一版 ``run_publish``，汇成一个
  持久**只读**草稿池 ``{slug}_drafts_{platform}.json`` = 数组 ``[{draft_id, headline, body}]``。
  一次生成、整份覆盖（重新扇出 = 显式重掷全部 persona）。「选中」不在本层——本层只产池。
- **复数视角合并**（``--combine a,b``，上限 2）：把两份既有草稿合并成一条 append 进池：
  - 路线 A（``--combine-mode A``，生产默认）：把两份蒸馏视角拼成复合 ``persona_perspective``
    再跑一次 ``run_publish``——同一条创作管线，多花一次 LLM 调用但出稿浑然一体。
  - 路线 B（``--combine-mode B``）：读池内两份既有 body 走 ``combine_bodies`` 纯函数融合，
    不调 LLM、省一次调用，但接缝 / 调性一致性存疑。
  - ``--combine-mode both``（**仅 GATE 离线对照**）：一次产 ``a+b#A`` + ``a+b#B`` 两版
    append，供总编肉眼并列二选一；生产链路永不传 both（serve 恒调单版）。

本层不碰 selection.json、不派生当前稿、不失效 humanized——那些是「选中」语义，属 serve
（10.4）的 ``/api/select-draft`` 职责。本层纯粹「产只读来源池」。
``run_publish`` / ``load_persona_perspective`` 可注入，测试用 stub 免真调 LLM。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import compose
from review_panel.publish_adapter import (
    _attach_movie_header,
    _default_batch_root,
    find_candidate,
    load_judge_entry,
    load_news,
    locate_news_dir,
)

_MAX_COMBINE = 2

# 中性默认稿的 draft_id：不注入任何 persona 主视角（persona_perspective=""）跑一版，
# 排在草稿池第一条。面板默认预览 drafts[0]（review_panel/index.html），故它即
# 「编辑打开先看到的默认稿」；per-persona 各版作为加了脾气滤镜的备选跟在后面。
_DEFAULT_DRAFT_ID = "混合视角"


def _drafts_path(news_dir: Path, slug: str, platform: str) -> Path:
    """草稿池文件：与 ``{slug}_copy_{platform}.md`` 同目录（news_dir.parent）。"""
    return news_dir.parent / f"{slug}_drafts_{platform}.json"


def _read_pool(path: Path) -> list[dict[str, Any]]:
    """读既有草稿池；不存在 → 空列表。"""
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _write_pool(path: Path, pool: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _draft_entry(draft_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    """归一化池条目：{draft_id, headline, body}（ADR-0017 D3），非空 warnings 时追加保留。

    Phase 12.5：``run_publish`` 重试耗尽仍命中 body_lint / judge 违规时会在返回值挂
    ``warnings``；池条目原样透传该字段供编辑面板标注、手动再触发 retry。空/无 warnings
    的既有条目不加键，保持池结构零回归。
    """
    entry: dict[str, Any] = {
        "draft_id": draft_id,
        "headline": str(draft.get("headline") or "").strip(),
        "body": str(draft.get("body") or "").strip(),
    }
    warnings = draft.get("warnings")
    if warnings:
        entry["warnings"] = warnings
    return entry


def _candidate_personas(candidate: dict[str, Any]) -> list[str]:
    """Collect persona ids for draft fan-out.

    Prefer candidate.triggered_by when it already contains the full persona set,
    but fall back to persona-semantic hit_sources so truncated triggered_by data
    does not collapse an 8-hit candidate down to the first few personas.
    """
    personas = _dedupe_personas(candidate.get("triggered_by"))
    seen = set(personas)
    for source in candidate.get("hit_sources") or []:
        if not isinstance(source, dict):
            continue
        if str(source.get("search_unit_kind") or "").strip().lower() != "persona-semantic":
            continue
        agent_id = str(source.get("agent_id") or "").strip()
        if not agent_id or agent_id in seen:
            continue
        seen.add(agent_id)
        personas.append(agent_id)
    return personas


def _dedupe_personas(triggered_by: Any) -> list[str]:
    """triggered_by 去重且保序；非 str 项跳过。"""
    seen: set[str] = set()
    result: list[str] = []
    for item in triggered_by or []:
        if not isinstance(item, str):
            continue
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def combine_bodies(body_a: str, body_b: str) -> str:
    """路线 B 文本融合纯函数：两份既有 body → 一份融合 body（不调 LLM）。

    独立可测、便于 GATE 迭代融合策略。当前策略保守：保留 a 的归属行（首行，ADR-0015 D3），
    其后接 a、b 正文主体，用空行分隔——不重排、不改写，只做无损拼接，把「接缝与调性一致性」
    的判断权交给 GATE 肉眼对照（路线 B 的已知局限）。
    """
    a = (body_a or "").strip()
    b = (body_b or "").strip()
    if not a:
        return b
    if not b:
        return a
    a_lines = a.splitlines()
    attribution = a_lines[0].strip()
    a_rest = "\n".join(a_lines[1:]).strip()
    # b 若以同一归属行开头（同片），去掉 b 的重复归属行，避免片名 / 年 / 导演出现两次。
    b_lines = b.splitlines()
    b_rest = b
    if b_lines and b_lines[0].strip() == attribution:
        b_rest = "\n".join(b_lines[1:]).strip()
    segments = [seg for seg in (a_rest, b_rest) if seg]
    return "\n\n".join([attribution, *segments]) if attribution else "\n\n".join(segments)


def run_fanout(
    date: str,
    slug: str,
    tmdb_id: int | str,
    *,
    provider: str | None = None,
    platform: str = "xiaohongshu",
    batch_root: Path | None = None,
    run_publish: Any = compose.run_publish,
    load_persona_perspective: Any = compose.load_persona_perspective,
    judge_llm_call: Any = None,
    max_body_retries: int = 1,
) -> Path:
    """全量扇出 orchestrator：池首中性默认稿 + triggered_by 每 persona 各注入蒸馏视角一版 → 整份覆盖池。

    池首固定放一条**中性默认稿**（``persona_perspective=""``，不注入任何原型主视角），
    作为编辑打开面板先看到的默认版；其后按 triggered_by 逐 persona 各出一版加了脾气的备选。
    ``run_publish`` / ``load_persona_perspective`` 可注入（默认 ``compose`` 真实函数），
    测试用 stub 替换免真调 LLM。返回草稿池文件路径。

    ``judge_llm_call`` / ``max_body_retries``（Phase 12.5）逐份透传给 ``run_publish``，
    接入 12.4 已建好的正文质量双闸门：body_lint 无条件跑，judge 仅当注入非 None 的
    ``judge_llm_call`` 时才跑。默认 ``judge_llm_call=None`` → 与之前行为完全一致
    （只跑 body_lint），既有测试零回归。
    """
    root = batch_root or _default_batch_root()
    news_dir = locate_news_dir(date, slug, batch_root=root)
    news = load_news(news_dir)
    candidate = find_candidate(news_dir, tmdb_id)
    judge = load_judge_entry(news_dir, tmdb_id)

    personas = _candidate_personas(candidate)
    if not personas:
        raise ValueError(
            f"candidate tmdb_id {tmdb_id!r} has empty triggered_by; nothing to fan out"
        )

    def _run_one(persona_perspective: str, draft_id: str) -> dict[str, Any]:
        draft = run_publish(
            candidate,
            news,
            provider=provider,
            judge=judge,
            platform=platform,
            persona_perspective=persona_perspective,
            judge_llm_call=judge_llm_call,
            max_body_retries=max_body_retries,
        )
        draft = dict(draft)
        draft["body"] = _attach_movie_header(candidate, draft.get("body", ""))
        return _draft_entry(draft_id, draft)

    # 池首：中性默认稿（不注入主视角）。面板默认预览 drafts[0]，故它即默认稿。
    pool: list[dict[str, Any]] = [_run_one("", _DEFAULT_DRAFT_ID)]
    for persona in personas:
        # draft_id = 归一化后的 persona 名（The-Sage），与 c2_perspective 目录一致、可读。
        normalized = "-".join(part.capitalize() for part in persona.split("-"))
        pool.append(_run_one(load_persona_perspective(persona), normalized))

    # 整份覆盖（ADR-0017 D3：重新扇出 = 显式重掷池首中性默认 + 全部 persona）。
    drafts_path = _drafts_path(news_dir, slug, platform)
    _write_pool(drafts_path, pool)
    return drafts_path


def run_combine(
    date: str,
    slug: str,
    tmdb_id: int | str,
    draft_ids: list[str],
    *,
    combine_mode: str = "A",
    provider: str | None = None,
    platform: str = "xiaohongshu",
    batch_root: Path | None = None,
    run_publish: Any = compose.run_publish,
    load_persona_perspective: Any = compose.load_persona_perspective,
) -> Path:
    """复数视角合并 orchestrator（上限 2）：把两份既有草稿合并成一条 append 进池。

    ``combine_mode``：``A`` 重跑 C2 合并视角、``B`` 文本融合既有 body、``both`` 产两版
    （``a+b#A`` + ``a+b#B``，仅 GATE 离线对照）。**append-only**：读池 → append → 写回，
    不动其它草稿（ADR-0017 D3/D5）。
    """
    ids = [i.strip() for i in draft_ids if i and i.strip()]
    if len(ids) != _MAX_COMBINE:
        raise ValueError(
            f"combine requires exactly {_MAX_COMBINE} draft_ids (≤2 硬约束), got {len(ids)}: {ids}"
        )
    if combine_mode not in ("A", "B", "both"):
        raise ValueError(f"unknown combine_mode {combine_mode!r}, expected A|B|both")

    root = batch_root or _default_batch_root()
    news_dir = locate_news_dir(date, slug, batch_root=root)
    news = load_news(news_dir)
    candidate = find_candidate(news_dir, tmdb_id)
    judge = load_judge_entry(news_dir, tmdb_id)

    drafts_path = _drafts_path(news_dir, slug, platform)
    pool = _read_pool(drafts_path)
    by_id = {str(d.get("draft_id")): d for d in pool if isinstance(d, dict)}
    a_id, b_id = ids
    for want in ids:
        if want not in by_id:
            raise ValueError(
                f"combine target {want!r} not found in pool {drafts_path.name}; "
                f"available: {', '.join(by_id) or '（空池）'}"
            )
    base_id = f"{a_id}+{b_id}"

    def _route_a() -> dict[str, Any]:
        # 复合视角：两份蒸馏视角拼接成一个 persona_perspective 再跑 run_publish。
        composite = "\n\n".join(
            load_persona_perspective(pid) for pid in ids
        )
        return run_publish(
            candidate,
            news,
            provider=provider,
            judge=judge,
            platform=platform,
            persona_perspective=composite,
        )

    def _route_b() -> dict[str, Any]:
        # 文本融合：读池内两份既有 body 走纯函数，不调 LLM。headline 取 a 的既有 headline。
        merged_body = combine_bodies(by_id[a_id].get("body", ""), by_id[b_id].get("body", ""))
        return {"headline": by_id[a_id].get("headline", ""), "body": _attach_movie_header(candidate, merged_body)}

    if combine_mode == "A":
        pool.append(_draft_entry(base_id, _route_a()))
    elif combine_mode == "B":
        pool.append(_draft_entry(base_id, _route_b()))
    else:  # both：GATE 离线对照，产 #A / #B 两版
        pool.append(_draft_entry(f"{base_id}#A", _route_a()))
        pool.append(_draft_entry(f"{base_id}#B", _route_b()))

    _write_pool(drafts_path, pool)
    return drafts_path


def _parse_combine(raw: str | None) -> list[str]:
    """解析 ``--combine a,b`` 逗号列表，去空白项。校验 ≤2 留给 run_combine。"""
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fan out a daily_batch candidate's triggered_by personas into a "
        "read-only draft pool {slug}_drafts_{platform}.json, or combine ≤2 drafts.",
    )
    parser.add_argument("--date", required=True, help="日期，如 2026-07-06")
    parser.add_argument("--news-slug", dest="news_slug", required=True, help="新闻目录 slug")
    parser.add_argument("--tmdb-id", dest="tmdb_id", required=True, help="选定候选的 tmdb_id")
    parser.add_argument("--provider", choices=["mimo", "deepseek"], default=None)
    parser.add_argument(
        "--platform",
        choices=["xiaohongshu"],
        default="xiaohongshu",
        help="发布平台（默认 xiaohongshu），透传给 compose.run_publish。",
    )
    parser.add_argument(
        "--combine",
        default=None,
        help="合并模式：逗号分隔的两个 draft_id（如 The-Sage,The-Explorer），上限 2。",
    )
    parser.add_argument(
        "--combine-mode",
        dest="combine_mode",
        choices=["A", "B", "both"],
        default="A",
        help="合并路线：A 重跑 C2 合并视角（生产默认）/ B 文本融合 / both 产两版（仅 GATE 离线对照）。",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        default=False,
        help=(
            "接入 12.4 正文质量 judge 闸门：用 compose.make_real_llm_call(provider) "
            "构造真实 judge_llm_call 传给 run_fanout（默认关闭，只跑 body_lint）。"
        ),
    )
    parser.add_argument(
        "--max-body-retries",
        dest="max_body_retries",
        type=int,
        default=1,
        help="正文质量闸门命中后的最大重试次数，透传给 run_publish（默认 1）。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    combine_ids = _parse_combine(args.combine)
    try:
        if combine_ids:
            pool_path = run_combine(
                args.date,
                args.news_slug,
                args.tmdb_id,
                combine_ids,
                combine_mode=args.combine_mode,
                provider=args.provider,
                platform=args.platform,
            )
        else:
            judge_llm_call = (
                compose.make_real_llm_call(provider=args.provider) if args.judge else None
            )
            pool_path = run_fanout(
                args.date,
                args.news_slug,
                args.tmdb_id,
                provider=args.provider,
                platform=args.platform,
                judge_llm_call=judge_llm_call,
                max_body_retries=args.max_body_retries,
            )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    print(f"Wrote {pool_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())