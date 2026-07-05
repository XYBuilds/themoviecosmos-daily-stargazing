"""daily_batch.py · Daily Batch 编排器 + 断点续跑 (Phase 7.2).

链路（复用 Phase 6 单条管线的下层 stage 函数，语义与 main.py 保持一致）:

  heat_pool.fetch_heat_pool() → batch_state 初始化
    → for each item:
        deconstruct(A0) → expand(P-Expand，可 --skip-expand)
        → persona_pipeline × N（可 --personas 限制，逐个 persona 落盘 checkpoint）
        → retrieve_from_agents → compose.run_review(C1) → briefing.md
        → 每完成一个 stage / persona 立即原子写 state/daily_batch_{date}.json

状态流转：pending → deconstruct → expand → persona → retrieve → compose → done

断点续跑：
  - item 级：status == "done" 的 item 直接跳过。
  - stage 级：已完成的 stage 产物（deconstruct.json / expand.json / retrieve.json /
    briefing.md）落在 output/daily_batch/{date}/{NN}-{slug}/ 下，resume 时优先从磁盘
    加载，不重新调用 LLM。
  - persona 级：personas/{persona_id}.json 存在且 persona_id 已在
    state.items[i].completed_personas 中时跳过，只补跑剩余 persona。

产出目录：output/daily_batch/{date}/{NN}-{slug}/
State 文件：state/daily_batch_{date}.json（.tmp + os.replace 原子写）
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import compose
from scripts.agents import NewsItem, news_to_dict
from scripts.extract import run_deconstruct
from scripts.heat_pool import DEFAULT_MIN_COUNT, fetch_heat_pool, pool_output_path
from scripts.lib.paths import repo_root, state_dir
from scripts.lib.run_options import RunOptions
from scripts.retrieve import retrieve_from_agents
from scripts.rewrite import list_persona_ids, pipeline_result_to_dict, run_persona_pipeline

# 状态流转顺序（用于日志 / 校验，实际续跑判断以磁盘产物 + completed_personas 为准）。
STAGE_ORDER: tuple[str, ...] = (
    "pending",
    "deconstruct",
    "expand",
    "persona",
    "retrieve",
    "compose",
    "done",
)

_SLUG_WORD_COUNT = 6
_SLUG_STRIP_RE = re.compile(r"[^a-z0-9\s-]")
_SLUG_WS_RE = re.compile(r"\s+")


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


def slugify(title: str, *, max_words: int = _SLUG_WORD_COUNT) -> str:
    """title → lowercase，去标点，取前 max_words 个词，连字符连接。

    空标题 / 全标点标题回退为 "untitled"，保证目录名永不为空。
    """
    lowered = (title or "").strip().lower()
    cleaned = _SLUG_STRIP_RE.sub("", lowered)
    words = [w for w in _SLUG_WS_RE.split(cleaned.strip()) if w]
    slug = "-".join(words[:max_words])
    return slug or "untitled"


def _today_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def batch_output_dir(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (repo_root() / "output" / "daily_batch")
    return base / date


def item_dir(date: str, index: int, slug: str, out_dir: Path | None = None) -> Path:
    return batch_output_dir(date, out_dir) / f"{index + 1:02d}-{slug}"


def state_path(date: str, base_state_dir: Path | None = None) -> Path:
    base = base_state_dir if base_state_dir is not None else state_dir()
    return base / f"daily_batch_{date}.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """原子写：先写 .tmp，再 os.replace，避免中断产出半截 state 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class BatchItemState:
    """单条 news 的批处理状态（对应 state.items[i]）。"""

    index: int
    url: str
    title: str
    slug: str
    status: str = "pending"
    last_completed_stage: str | None = None
    completed_personas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "url": self.url,
            "title": self.title,
            "slug": self.slug,
            "status": self.status,
            "last_completed_stage": self.last_completed_stage,
            "completed_personas": list(self.completed_personas),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchItemState":
        return cls(
            index=int(data["index"]),
            url=str(data.get("url") or ""),
            title=str(data.get("title") or ""),
            slug=str(data.get("slug") or ""),
            status=str(data.get("status") or "pending"),
            last_completed_stage=data.get("last_completed_stage"),
            completed_personas=list(data.get("completed_personas") or []),
        )


@dataclass
class BatchState:
    """整个 daily batch 的状态（对应 state/daily_batch_{date}.json）。"""

    date: str
    pool_file: str
    created_at: str
    items: list[BatchItemState] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "pool_file": self.pool_file,
            "created_at": self.created_at,
            "items": [it.to_dict() for it in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchState":
        return cls(
            date=str(data["date"]),
            pool_file=str(data.get("pool_file") or ""),
            created_at=str(data.get("created_at") or ""),
            items=[BatchItemState.from_dict(it) for it in data.get("items") or []],
        )

    def save(self, path: Path) -> None:
        _atomic_write_json(path, self.to_dict())


def init_batch_state(date: str, pool: list[dict[str, Any]], pool_file: str) -> BatchState:
    """从 heat_pool 的 ranked pool 构造初始 batch_state（全部 pending）。"""
    items = [
        BatchItemState(
            index=idx,
            url=str(entry.get("url") or ""),
            title=str(entry.get("title") or ""),
            slug=slugify(str(entry.get("title") or "")),
        )
        for idx, entry in enumerate(pool)
    ]
    return BatchState(
        date=date,
        pool_file=pool_file,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        items=items,
    )


def load_batch_state(path: Path) -> BatchState:
    return BatchState.from_dict(_read_json(path))


def _news_item_for_pool_entry(entry: dict[str, Any]) -> NewsItem:
    return NewsItem(
        title=str(entry.get("title") or ""),
        description=str(entry.get("description") or ""),
        pub_time=str(entry.get("pub_time") or ""),
        source_name=str(entry.get("source_name") or "Guardian"),
        url=str(entry.get("url") or ""),
    )


def _persona_result_to_agent(result: Any) -> dict[str, Any]:
    """Mirror main._persona_result_to_agent (agents_list entry for retrieve)."""
    payload = pipeline_result_to_dict(result)
    pseudos = payload.get("pseudos") or []
    agent: dict[str, Any] = {
        "agent_id": result.persona_id,
        "persona_name": result.persona_id,
        "role": "persona",
        "pseudos": pseudos,
        "text": str(pseudos[0].get("text", "")) if pseudos else "",
        "warnings": list(result.warnings or []),
    }
    if payload.get("search_units"):
        agent["search_units"] = payload["search_units"]
    if payload.get("fragment_ladders"):
        agent["fragment_ladders"] = payload["fragment_ladders"]
    return agent


def _persona_agent_dict_to_dict(agent: dict[str, Any]) -> dict[str, Any]:
    """personas/{id}.json 落盘的是 pipeline_result_to_dict() payload 加 agent 视图，
    resume 时直接把落盘的 agent 视图原样喂回 agents_list（无需还原 PersonaPipelineResult）。
    """
    return agent


async def _process_item(
    entry: dict[str, Any],
    item_state: BatchItemState,
    item_out_dir: Path,
    *,
    provider: str | None,
    run_options: RunOptions,
    batch_state: BatchState,
    state_file: Path,
) -> None:
    """跑单条 news 的完整 stage 链，每个 stage / persona 后立即 checkpoint。

    resume 时：deconstruct/expand/retrieve/compose 的产物文件存在即直接加载，跳过重跑；
    persona 逐个检查 personas/{id}.json 是否已存在于 completed_personas 中。
    """
    if item_state.status == "done":
        return

    news = _news_item_for_pool_entry(entry)
    item_out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(item_out_dir / "news.json", news_to_dict(news))

    # --- Stage: deconstruct(A0) ---
    deconstruct_path = item_out_dir / "deconstruct.json"
    if deconstruct_path.is_file():
        deconstruction = _read_json(deconstruct_path)
    else:
        _progress(f"[item {item_state.index}] deconstruct start")
        decon_payload = run_deconstruct(news, provider=provider)
        deconstruction = decon_payload.get("deconstruction")
        if not isinstance(deconstruction, dict) or not deconstruction:
            raise ValueError(f"item {item_state.index}: deconstruct failed — no valid deconstruction")
        _write_json(deconstruct_path, deconstruction)
        item_state.status = "deconstruct"
        item_state.last_completed_stage = "deconstruct"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] deconstruct done")

    # --- Stage: expand(P-Expand) ---
    expand_path = item_out_dir / "expand.json"
    if run_options.skip_expand:
        expansion: dict[str, Any] | None = None
    elif expand_path.is_file():
        expansion = _read_json(expand_path)
    else:
        from scripts.expand import run_expansion

        _progress(f"[item {item_state.index}] expand start")
        expansion_payload = run_expansion(deconstruction, provider=provider)
        expansion = expansion_payload.get("expansion")
        if not isinstance(expansion, dict):
            expansion = None
        _write_json(expand_path, expansion or {})
        item_state.status = "expand"
        item_state.last_completed_stage = "expand"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] expand done")

    # --- Stage: persona × N (per-persona checkpoint) ---
    personas_dir = item_out_dir / "personas"
    persona_ids = list_persona_ids()
    if run_options.persona_limit is not None:
        persona_ids = persona_ids[: run_options.persona_limit]

    errors: list[dict[str, Any]] = []
    agents_list: list[dict[str, Any]] = []
    completed = set(item_state.completed_personas)

    for idx, persona_id in enumerate(persona_ids, start=1):
        persona_json_path = personas_dir / f"{persona_id}.json"
        if persona_id in completed and persona_json_path.is_file():
            cached = _read_json(persona_json_path)
            if cached.get("error"):
                errors.append({"agent_id": persona_id, "message": cached["error"]})
            else:
                agents_list.append(_persona_agent_dict_to_dict(cached["agent"]))
            continue

        _progress(f"[item {item_state.index}] persona {idx}/{len(persona_ids)} {persona_id} start")
        result = await run_persona_pipeline(
            persona_id,
            deconstruction,
            provider=provider,
            expansion=expansion,
        )
        if result.error or not result.pseudos:
            error_message = result.error or "no pseudos"
            errors.append({"agent_id": persona_id, "message": error_message})
            _write_json(persona_json_path, {"error": error_message})
        else:
            agent = _persona_result_to_agent(result)
            agents_list.append(agent)
            _write_json(persona_json_path, {"agent": agent})

        if persona_id not in item_state.completed_personas:
            item_state.completed_personas.append(persona_id)
        item_state.status = "persona"
        item_state.last_completed_stage = "expand" if item_state.last_completed_stage in (None, "deconstruct") else item_state.last_completed_stage
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] persona {idx}/{len(persona_ids)} {persona_id} done")

    item_state.last_completed_stage = "persona"
    item_state.status = "persona"
    batch_state.save(state_file)

    # --- Stage: retrieve ---
    retrieve_path = item_out_dir / "retrieve.json"
    if retrieve_path.is_file():
        retrieve_result = _read_json(retrieve_path)
    else:
        _progress(f"[item {item_state.index}] retrieve start")
        retrieve_result = retrieve_from_agents(agents_list, errors, top_k=run_options.judge_topk)
        _write_json(retrieve_path, retrieve_result)
        item_state.status = "retrieve"
        item_state.last_completed_stage = "retrieve"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] retrieve done")

    # --- Stage: compose(C1) + briefing ---
    briefing_path = item_out_dir / "briefing.md"
    if not briefing_path.is_file():
        _progress(f"[item {item_state.index}] compose start")
        news_dict = news_to_dict(news)
        review_result = compose.run_review(retrieve_result, news_dict, provider=provider)
        for err in review_result.errors:
            errors.append({"agent_id": "C1", "message": err.get("message", str(err))})
        briefing_md = _build_item_briefing(item_state.index, news_dict, errors, retrieve_result, review_result)
        briefing_path.parent.mkdir(parents=True, exist_ok=True)
        briefing_path.write_text(briefing_md, encoding="utf-8")
        item_state.status = "compose"
        item_state.last_completed_stage = "compose"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] compose done")

    item_state.status = "done"
    item_state.last_completed_stage = "compose"
    batch_state.save(state_file)


def _build_item_briefing(
    index: int,
    news_dict: dict[str, Any],
    errors: list[dict[str, Any]],
    retrieve_result: dict[str, Any],
    review_result: Any,
) -> str:
    """单条 item 的简化 Markdown（daily_batch 场景下每条各自独立成文件）。"""
    candidates = retrieve_result.get("candidates") or []
    lines = [f"# Daily Batch item {index + 1:02d}", ""]
    lines.append(f"- title: {news_dict.get('title', '')}")
    lines.append(f"- url: {news_dict.get('url', '')}")
    lines.append("")
    lines.append("## Candidates")
    for cand in candidates:
        title = cand.get("title")
        year = cand.get("release_year")
        tmdb_id = cand.get("tmdb_id")
        lines.append(f"- {title} ({year}) [tmdb:{tmdb_id}]")
    if not candidates:
        lines.append("（无候选）")
    lines.append("")
    lines.append("## Review copies")
    for copy in getattr(review_result, "review_copies", []) or []:
        text = getattr(copy, "judge_rationale_zh", "") or getattr(copy, "judge_causal_test_zh", "") or ""
        lines.append(f"- tmdb:{copy.tmdb_id}: {text}")
    if errors:
        lines.append("")
        lines.append("## Errors")
        for err in errors:
            lines.append(f"- {err.get('agent_id')}: {err.get('message')}")
    lines.append("")
    return "\n".join(lines)


async def run_daily_batch(
    *,
    date: str | None = None,
    resume: bool = False,
    min_count: int = DEFAULT_MIN_COUNT,
    run_options: RunOptions | None = None,
    provider: str | None = None,
    out_dir: Path | None = None,
    base_state_dir: Path | None = None,
) -> BatchState:
    """顶层入口：非 resume 时先跑 heat_pool 选题并初始化 state；resume 时加载既有 state，
    跳过 done 的 item，从断点继续。逐条处理 items，每完成 stage/persona 立即落盘 checkpoint。
    """
    resolved_date = date or _today_iso()
    resolved_run_options = run_options or RunOptions()
    resolved_state_path = state_path(resolved_date, base_state_dir)

    if resume:
        if not resolved_state_path.is_file():
            raise ValueError(f"--resume requested but no state file found: {resolved_state_path}")
        batch_state = load_batch_state(resolved_state_path)
        pool_file_path = Path(batch_state.pool_file)
        if not pool_file_path.is_absolute():
            pool_file_path = repo_root() / pool_file_path
        pool = _read_json(pool_file_path)
    else:
        pool = fetch_heat_pool(date=resolved_date, min_count=min_count, out_dir=out_dir)
        pool_file_path = pool_output_path(resolved_date, out_dir)
        batch_state = init_batch_state(resolved_date, pool, str(pool_file_path))
        batch_state.save(resolved_state_path)

    for item_state in batch_state.items:
        if item_state.index >= len(pool):
            continue
        entry = pool[item_state.index]
        target_dir = item_dir(resolved_date, item_state.index, item_state.slug, out_dir)
        await _process_item(
            entry,
            item_state,
            target_dir,
            provider=provider,
            run_options=resolved_run_options,
            batch_state=batch_state,
            state_file=resolved_state_path,
        )

    return batch_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the daily batch orchestrator: heat pool → N news → daily pipeline, "
        "with stage+persona level checkpointing and resume.",
    )
    parser.add_argument("--date", help="Batch date override (default: today, UTC, YYYY-MM-DD).")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing state file.")
    parser.add_argument(
        "--min-count",
        type=int,
        default=DEFAULT_MIN_COUNT,
        metavar="N",
        help=f"Minimum heat pool size after fallback (default: {DEFAULT_MIN_COUNT}).",
    )
    parser.add_argument(
        "--personas",
        type=int,
        default=None,
        metavar="N",
        help="Dev shortcut: only run the first N personas per item (default: all 12).",
    )
    parser.add_argument("--skip-expand", action="store_true", help="Dev shortcut: skip the P-Expand stage.")
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_options = RunOptions(persona_limit=args.personas, skip_expand=args.skip_expand)
    try:
        asyncio.run(
            run_daily_batch(
                date=args.date,
                resume=args.resume,
                min_count=args.min_count,
                run_options=run_options,
                provider=args.provider,
            )
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())