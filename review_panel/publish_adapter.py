"""publish_adapter.py · Phase 8.2 · daily_batch → C2 定稿薄适配脚本.

现有 ``scripts/main.py publish`` 消费的是 Phase6 单条模式产物
（``output/Daily_Briefing/{date}.md`` + ``{date}_candidates.json``），而
daily_batch 产物落在 ``output/daily_batch/{date}/{slug}/``（news.json /
retrieve.json / llm-judge-scores.json），结构不同、无法直接复用那两个定位函数。

本脚本直接从 daily_batch 目录取 news + candidate，调用**稳定的**
``scripts.compose.run_publish`` 产出定稿 ``_copy.md``。耦合收敛在本单文件：
只有这里 import ``scripts.compose``（``compose`` 本身只依赖 openai/movie_metadata，
不会像 ``scripts.main`` 那样透传拉入 extract/retrieve/rewrite/fetch_news 等重依赖），
不引入其它项目内部耦合。

因此本文件的 ``render_copy_markdown`` 不复用 ``scripts.main.build_copy_markdown``：
import ``scripts.main`` 会连带 import ``scripts.extract`` / ``scripts.retrieve`` /
``scripts.rewrite`` / ``scripts.fetch_news``（检索索引、persona pipeline 等重模块），
与 plan 里「耦合收敛在本单文件、只 import scripts.compose」的约束冲突，
故自带一份风格等价的轻量渲染函数。
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
from scripts.compose import JudgeEntry
from scripts.lib.paths import repo_root


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def locate_news_dir(date: str, slug: str, batch_root: Path | None = None) -> Path:
    """定位 ``{batch_root}/{date}/{slug}/``；目录或 news.json 缺失 → 清晰报错。"""
    root = batch_root or _default_batch_root()
    news_dir = root / date / slug
    if not news_dir.is_dir():
        raise ValueError(f"news dir not found: {news_dir}")
    if not (news_dir / "news.json").is_file():
        raise ValueError(f"news.json not found in {news_dir}")
    return news_dir


def load_news(news_dir: Path) -> dict[str, str]:
    """读 news.json；只保留 compose.run_publish 需要的 title/description/url。"""
    data = _read_json(news_dir / "news.json")
    return {
        "title": str(data.get("title", "") or "").strip(),
        "description": str(data.get("description", "") or "").strip(),
        "url": str(data.get("url", "") or "").strip(),
    }


def find_candidate(news_dir: Path, tmdb_id: int | str) -> dict[str, Any]:
    """按 tmdb_id（str() 归一化）在 retrieve.json 的 candidates 里定位候选。

    CLI 传入的 tmdb_id 可能是 int 或 str，retrieve.json 里的 candidate.tmdb_id 是
    int；str() 归一化后比较，避免类型不一致导致永远匹配不到。
    """
    retrieve = _read_json(news_dir / "retrieve.json")
    candidates = retrieve.get("candidates") or []
    target = str(tmdb_id)
    for cand in candidates:
        if isinstance(cand, dict) and str(cand.get("tmdb_id")) == target:
            return cand
    available = ", ".join(str(c.get("tmdb_id")) for c in candidates if isinstance(c, dict))
    raise ValueError(
        f"tmdb_id {tmdb_id!r} not found among candidates in {news_dir / 'retrieve.json'}; "
        f"available tmdb_ids: {available or '（无候选）'}"
    )


def load_judge_entry(news_dir: Path, tmdb_id: int | str) -> JudgeEntry | None:
    """读 llm-judge-scores.json，按 tmdb_id（str 归一化）找 judge 行。

    judge 文件整体缺失，或该 tmdb_id 未被 judge 覆盖，都是正常业务状态（judge 只对
    部分候选抽样评分），因此容错返回 None 而不是抛异常。
    """
    judge_path = news_dir / "llm-judge-scores.json"
    if not judge_path.is_file():
        return None
    data = _read_json(judge_path)
    target = str(tmdb_id)
    for row in data.get("scores") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("tmdb_id")) != target:
            continue
        raw_score = row.get("judge_score")
        score = int(raw_score) if isinstance(raw_score, (int, float)) else None
        return JudgeEntry(
            score=score,
            rationale=str(row.get("rationale", "") or ""),
            causal_test=str(row.get("causal_test", "") or ""),
            resonance_type=str(row.get("judge_resonance_type", "") or ""),
        )
    return None


def render_copy_markdown(
    date: str,
    candidate: dict[str, Any],
    news: dict[str, str],
    draft: dict[str, Any],
) -> str:
    """渲染 ``_copy.md``：headline / 中文发布正文 / 新闻原文 / 链接四段。

    ADR-0015 D3/D4：消费创作环节产出的 ``draft["headline"]`` 作醒目标题；**不再**用
    ``{title}({year})`` 另拼机械标题行——电影真名已由正文首行的 `「片名」(YYYY) 导演名`
    归属行承载，避免重复。自带而非 import ``scripts.main`` 的理由见本文件模块 docstring。
    """
    headline = str(draft.get("headline") or "").strip()
    movie_url = str(candidate.get("movie_url") or "")
    news_url = str(news.get("url") or "")
    body = str(draft.get("body") or "").strip()

    lines = [
        f"# 发布定稿 · {date} · 小红书",
        "",
        "## 小红书标题（headline）",
        "",
        headline or "（无标题）",
        "",
        "## 中文发布正文",
        "",
        body or "（无正文）",
        "",
        "## 新闻原文（English source）",
        "",
        f"**{news.get('title', '')}**",
        "",
        str(news.get("description", "")),
        "",
        "## 链接",
        "",
        f"- 电影: {movie_url or '（无）'}",
        f"- 新闻: {news_url or '（无）'}",
        "",
    ]
    return "\n".join(lines)


def run_adapter(
    date: str,
    slug: str,
    tmdb_id: int | str,
    *,
    provider: str | None = None,
    platform: str = "xiaohongshu",
    batch_root: Path | None = None,
    run_publish: Any = compose.run_publish,
) -> Path:
    """薄适配 orchestrator：news+candidate+judge → run_publish → 写 ``_copy.md``。

    ``platform`` 透传给 ``run_publish``（ADR-0015 D1，默认 xiaohongshu——本期唯一平台）。
    ``run_publish`` 可注入（默认 ``compose.run_publish``），测试用 stub 替换，避免真调 LLM。
    """
    root = batch_root or _default_batch_root()
    news_dir = locate_news_dir(date, slug, batch_root=root)
    news = load_news(news_dir)
    candidate = find_candidate(news_dir, tmdb_id)
    judge = load_judge_entry(news_dir, tmdb_id)

    draft = run_publish(
        candidate, news, provider=provider, judge=judge, platform=platform
    )

    copy_path = news_dir.parent / f"{slug}_copy.md"
    copy_path.write_text(
        render_copy_markdown(date, candidate, news, draft), encoding="utf-8"
    )
    return copy_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish a daily_batch candidate's C2 draft as {slug}_copy.md.",
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        copy_path = run_adapter(
            args.date,
            args.news_slug,
            args.tmdb_id,
            provider=args.provider,
            platform=args.platform,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    print(f"Wrote {copy_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())