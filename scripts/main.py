"""main.py · 端到端每日星轨观测管线.

链路（对齐 .cursor/plans/Phase6-main-integration.plan.md Todo 6.2）:

  news(JSON/--url/--pick) → deconstruct(A0) → expand(P-Expand，可 --skip-expand)
  → persona_pipeline × N（可 --personas 限制）→ retrieve_from_agents
  → (可选) compose.run_review(C1) → 组装 Markdown → output/Daily_Briefing/{date}.md

CLI（日报管线，默认命令）:
  python scripts/main.py --news-file output/picked_news.json
  python scripts/main.py --url https://... --title "..." --description "..."
  python scripts/main.py --pick 3
  python scripts/main.py --news-file ... --date 2026-07-04
  python scripts/main.py --news-file ... --no-copy
  python scripts/main.py --news-file ... --personas 2

无参数时打印用法并以非 0 退出码结束。

CLI（``publish`` 子命令 · Todo 6.3，总编在日报候选中选定 1 部后定稿 C2）:
  python scripts/main.py publish --date 2026-07-04 --tmdb-id 157336

  读取 output/Daily_Briefing/{date}.md（新闻语境）+ {date}_candidates.json
  （候选池，按 tmdb_id 定位）→ compose.run_publish(candidate, news) → 写
  output/Daily_Briefing/{date}_copy.md。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import compose
from scripts.agents import NewsItem, load_news_from_file
from scripts.extract import run_deconstruct
from scripts.fetch_news import build_url_news_payload, fetch_guardian_api, mark_selected
from scripts.lib.render_briefing import _format_candidates_markdown, _format_errors, _format_reality_body
from scripts.lib.run_options import RunOptions
from scripts.retrieve import retrieve_from_agents
from scripts.rewrite import list_persona_ids, pipeline_result_to_dict, run_persona_pipeline


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


def _elapsed(start: float) -> str:
    return f"{time.perf_counter() - start:.1f}s"


def _news_from_dict(data: dict[str, Any]) -> NewsItem:
    """Build a NewsItem from a raw payload dict (mirrors agents.load_news_from_file)."""
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    if not title or not description:
        raise ValueError("news payload requires non-empty title and description")
    return NewsItem(
        title=title,
        description=description,
        pub_time=str(data.get("pub_time") or ""),
        source_name=str(data.get("source_name") or ""),
        url=str(data.get("url") or ""),
    )


def resolve_news(args: argparse.Namespace) -> NewsItem:
    """Resolve a NewsItem from --news-file / --url(+fallback) / --pick N."""
    if args.news_file:
        news_path = Path(args.news_file)
        if not news_path.is_absolute():
            news_path = _REPO_ROOT / news_path
        if not news_path.is_file():
            raise ValueError(f"news file not found: {news_path}")
        return load_news_from_file(news_path)

    if args.url:
        payload = build_url_news_payload(
            args.url,
            title=args.title,
            description=args.description,
        )
        mark_selected(payload)
        return _news_from_dict(payload)

    if args.pick is not None:
        candidates = fetch_guardian_api()
        pick_index = args.pick - 1
        if pick_index < 0 or pick_index >= len(candidates):
            raise ValueError(
                f"--pick {args.pick} is out of range; only {len(candidates)} candidate(s) available."
            )
        selected = candidates[pick_index]
        mark_selected(selected)
        return _news_from_dict(selected)

    raise ValueError("one of --news-file / --url / --pick is required")


def _persona_result_to_agent(result) -> dict[str, Any]:
    """Mirror run_eval._persona_result_to_agent (agents_list entry for retrieve)."""
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


async def run_daily_pipeline(
    news: NewsItem,
    *,
    provider: str | None,
    run_options: RunOptions,
) -> tuple[dict[str, Any], list[dict], dict[str, Any]]:
    """news → A0 → P-Expand → persona_pipeline × N → retrieve.

    Returns (news_dict, errors, retrieve_result).
    """
    stage_start = time.perf_counter()
    _progress("[stage 1/4] deconstruct(A0) start")
    decon_payload = run_deconstruct(news, provider=provider)
    deconstruction = decon_payload.get("deconstruction")
    if not isinstance(deconstruction, dict) or not deconstruction:
        raise ValueError("deconstruction failed — no valid deconstruction object")
    _progress(f"[stage 1/4] deconstruct(A0) done ({_elapsed(stage_start)})")

    if run_options.skip_expand:
        _progress("[stage 2/4] expand skipped (--skip-expand)")
        expansion = None
    else:
        from scripts.expand import run_expansion

        stage_start = time.perf_counter()
        _progress("[stage 2/4] expand start")
        expansion_payload = run_expansion(deconstruction, provider=provider)
        expansion = expansion_payload.get("expansion")
        if not isinstance(expansion, dict):
            expansion = None
        _progress(f"[stage 2/4] expand done ({_elapsed(stage_start)})")

    persona_ids = list_persona_ids()
    if run_options.persona_limit is not None:
        persona_ids = persona_ids[: run_options.persona_limit]

    errors: list[dict[str, Any]] = []
    agents_list: list[dict[str, Any]] = []
    stage_start = time.perf_counter()
    _progress(f"[stage 3/4] persona start total={len(persona_ids)}")
    for idx, persona_id in enumerate(persona_ids, start=1):
        persona_start = time.perf_counter()
        _progress(f"[persona {idx}/{len(persona_ids)}] {persona_id} start")
        result = await run_persona_pipeline(
            persona_id,
            deconstruction,
            provider=provider,
            expansion=expansion,
        )
        _progress(f"[persona {idx}/{len(persona_ids)}] {persona_id} done ({_elapsed(persona_start)})")
        if result.error or not result.pseudos:
            errors.append({"agent_id": persona_id, "message": result.error or "no pseudos"})
            continue
        agents_list.append(_persona_result_to_agent(result))
    _progress(f"[stage 3/4] persona done ({_elapsed(stage_start)})")

    stage_start = time.perf_counter()
    _progress("[stage 4/4] retrieve start")
    retrieve_result = retrieve_from_agents(agents_list, errors, top_k=run_options.judge_topk)
    _progress(f"[stage 4/4] retrieve done ({_elapsed(stage_start)})")

    from scripts.agents import news_to_dict

    return news_to_dict(news), errors, retrieve_result


def _format_oracle_appendix(retrieve_result: dict[str, Any]) -> str:
    """Render the A1 Reality Recorder (held-out oracle) appendix.

    Strictly isolated: only reads retrieve_result["a1_oracle"] /
    ["oracle_comparison"], never retrieve_result["candidates"] (production pool).
    This keeps A1 out of the candidate list, out of C1 input, and unselectable.
    """
    lines = ["## 附录 · A1 Reality Recorder（held-out oracle）", ""]
    a1_oracle = retrieve_result.get("a1_oracle")
    oracle_comparison = retrieve_result.get("oracle_comparison")

    if not a1_oracle:
        lines.append("（无 A1 oracle 数据 — baseline 查询未产生命中）")
        lines.append("")
        return "\n".join(lines)

    hit_ids = a1_oracle.get("hit_tmdb_ids") or []
    lines.append(f"- **A1 raw_hit_count**: {a1_oracle.get('raw_hit_count', 0)}")
    lines.append(f"- **A1 hit_tmdb_ids**: {', '.join(str(i) for i in hit_ids) or '—'}")

    if oracle_comparison:
        oracle_only = oracle_comparison.get("oracle_only") or oracle_comparison.get("a1_only") or []
        production_only = (
            oracle_comparison.get("production_only") or oracle_comparison.get("human_only") or []
        )
        lines.append(f"- **A1 召回但未进生产池**: {', '.join(str(i) for i in oracle_only) or '（无）'}")
        lines.append(f"- **生产池独有**: {', '.join(str(i) for i in production_only) or '（无）'}")
    lines.append("")
    return "\n".join(lines)


def _format_footer(retrieve_result: dict[str, Any]) -> str:
    """Render the meta footer from retrieve_result["meta"]."""
    meta = retrieve_result.get("meta") or {}
    lines = ["## 脚注", "", "- **meta**:"]
    for key in sorted(meta.keys()):
        lines.append(f"  - {key}: {meta[key]}")
    lines.append("")
    return "\n".join(lines)


def build_daily_briefing(
    date: str,
    news_dict: dict[str, Any],
    errors: list[dict[str, Any]],
    retrieve_result: dict[str, Any],
    *,
    review_copies: list[dict[str, Any]] | None = None,
) -> str:
    """Assemble the single Daily_Briefing Markdown string.

    Candidates come strictly from retrieve_result["candidates"] (the production
    pool); A1/oracle data (a1_oracle / oracle_comparison) is only ever read by
    _format_oracle_appendix and never mixed into the candidate list or C1 input.
    """
    news = NewsItem(
        title=str(news_dict.get("title") or ""),
        description=str(news_dict.get("description") or ""),
        pub_time=str(news_dict.get("pub_time") or ""),
        source_name=str(news_dict.get("source_name") or ""),
        url=str(news_dict.get("url") or ""),
    )
    candidates = retrieve_result.get("candidates") or []

    parts: list[str] = [f"# 每日星轨观测 · {date}", ""]
    parts.append(_format_reality_body(date, news))
    parts.append(_format_candidates_markdown(date, candidates, copies=review_copies))
    parts.append(_format_errors(errors))
    parts.append(_format_oracle_appendix(retrieve_result))
    parts.append(_format_footer(retrieve_result))
    return "\n".join(parts)


def _review_copies_payload(review_result) -> list[dict[str, Any]]:
    """Convert ReviewResult.review_copies into the list-of-dict shape that
    render_briefing._candidate_copy_text understands (tmdb_id + copy text).

    ReviewCopy has no single "copy text" field (Phase 6.1 legacy note about
    ``copy_text`` was inaccurate — see report); the Chinese-facing text is
    assembled from judge_rationale_zh here since that is the only authored
    Chinese narrative field on the card. This is a display convenience, not a
    change to compose.py's contract.
    """
    payload: list[dict[str, Any]] = []
    for copy in review_result.review_copies:
        text = copy.judge_rationale_zh or copy.judge_causal_test_zh or ""
        payload.append({"tmdb_id": copy.tmdb_id, "copy": text})
    return payload


def resolve_briefing_path(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (_REPO_ROOT / "output" / "Daily_Briefing")
    return base / f"{date}.md"


def resolve_candidates_path(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (_REPO_ROOT / "output" / "Daily_Briefing")
    return base / f"{date}_candidates.json"


def resolve_copy_path(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (_REPO_ROOT / "output" / "Daily_Briefing")
    return base / f"{date}_copy.md"


def _parse_news_from_briefing_md(text: str) -> dict[str, str]:
    """Recover the news dict compose.run_publish needs from the "现实波澜" section
    rendered by render_briefing._format_reality_body.

    Only title / description(summary) / url are needed — see
    compose.build_news_context, which is the only consumer of ``news`` inside
    run_publish.
    """
    title_match = re.search(r"^- \*\*title\*\*: (.*)$", text, re.MULTILINE)
    summary_match = re.search(r"^- \*\*summary\*\*: (.*)$", text, re.MULTILINE)
    url_match = re.search(r"^- news_url: (.*)$", text, re.MULTILINE)
    if not title_match or not summary_match:
        raise ValueError(
            "could not parse news title/summary out of the briefing markdown "
            "(expected the '## 现实波澜' section written by build_daily_briefing)"
        )
    url = url_match.group(1).strip() if url_match else ""
    return {
        "title": title_match.group(1).strip(),
        "description": summary_match.group(1).strip(),
        "url": "" if url in ("", "—") else url,
    }


def load_news_context_for_publish(date: str, out_dir: Path | None = None) -> dict[str, str]:
    """Load the news dict for ``publish`` from {date}.md (written by the daily pipeline)."""
    briefing_path = resolve_briefing_path(date, out_dir)
    if not briefing_path.is_file():
        raise ValueError(
            f"briefing not found: {briefing_path} "
            f"(run `python scripts/main.py --date {date} ...` first to produce it)"
        )
    return _parse_news_from_briefing_md(briefing_path.read_text(encoding="utf-8"))


def find_candidate_by_tmdb_id(
    date: str, tmdb_id: int, out_dir: Path | None = None
) -> dict[str, Any]:
    """Locate the candidate dict matching --tmdb-id inside {date}_candidates.json."""
    candidates_path = resolve_candidates_path(date, out_dir)
    if not candidates_path.is_file():
        raise ValueError(
            f"candidates file not found: {candidates_path} "
            f"(run `python scripts/main.py --date {date} ...` first to produce it)"
        )
    payload = json.loads(candidates_path.read_text(encoding="utf-8"))
    candidates = payload.get("candidates") or []
    for cand in candidates:
        if str(cand.get("tmdb_id")) == str(tmdb_id):
            return cand
    available = ", ".join(str(c.get("tmdb_id")) for c in candidates) or "（无候选）"
    raise ValueError(
        f"tmdb_id {tmdb_id} not found among candidates in {candidates_path}; "
        f"available tmdb_ids: {available}"
    )


def build_copy_markdown(
    date: str,
    candidate: dict[str, Any],
    news: dict[str, str],
    draft: dict[str, Any],
) -> str:
    """Render {date}_copy.md: C2's Chinese creative body (the only creative
    artifact per ADR-0012/ADR-0013) + the English news context it was written
    against + links.

    ``run_publish`` deliberately produces no English translation of the body
    (C2 is single-language Chinese prose by design). The "中英文两节" acceptance
    bar is satisfied by pairing the Chinese body with the original English news
    source it responds to, not by machine-translating the body itself — see
    report §4 for the reasoning.
    """
    title = str(candidate.get("title") or "")
    year = candidate.get("release_year")
    year_str = str(year) if year else "—"
    movie_url = str(candidate.get("movie_url") or "")
    news_url = str(news.get("url") or "")
    body = str(draft.get("body") or "").strip()

    lines = [
        f"# 发布定稿 · {date} · 《{title}》({year_str})",
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


def _run_publish_cli(args: argparse.Namespace) -> int:
    news = load_news_context_for_publish(args.date)
    candidate = find_candidate_by_tmdb_id(args.date, args.tmdb_id)
    draft = compose.run_publish(candidate, news, provider=args.provider)

    copy_md = build_copy_markdown(args.date, candidate, news, draft)
    copy_path = resolve_copy_path(args.date)
    copy_path.parent.mkdir(parents=True, exist_ok=True)
    copy_path.write_text(copy_md, encoding="utf-8")

    print(f"Wrote {copy_path.resolve()}", file=sys.stderr)
    return 0


def build_publish_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/main.py publish",
        description=(
            "Finalize the C2 publish copy for one editor-selected candidate "
            "(compose.run_publish) into output/Daily_Briefing/{date}_copy.md."
        ),
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Briefing date (YYYY-MM-DD); must match an existing {date}.md / _candidates.json pair.",
    )
    parser.add_argument(
        "--tmdb-id",
        required=True,
        type=int,
        metavar="ID",
        help="TMDB id of the candidate the editor selected from the daily briefing.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    return parser


async def _run_cli(args: argparse.Namespace) -> int:
    news = resolve_news(args)

    date = args.date or datetime.now(UTC).strftime("%Y-%m-%d")
    briefing_path = resolve_briefing_path(date)
    if briefing_path.is_file() and not args.force:
        print(
            f"error: briefing already exists: {briefing_path} (use --force to overwrite)",
            file=sys.stderr,
        )
        return 2

    run_options = RunOptions(
        persona_limit=args.personas,
        skip_expand=args.skip_expand,
        judge_topk=args.judge_topk,
        force=args.force,
    )

    news_dict, errors, retrieve_result = await run_daily_pipeline(
        news,
        provider=args.provider,
        run_options=run_options,
    )

    review_copies: list[dict[str, Any]] | None = None
    if not args.no_copy:
        stage_start = time.perf_counter()
        _progress("[stage 5/5] C1 review start")
        review_result = compose.run_review(retrieve_result, news_dict, provider=args.provider)
        if review_result.errors:
            for err in review_result.errors:
                errors.append({"agent_id": "C1", "message": err.get("message", str(err))})
        review_copies = _review_copies_payload(review_result)
        _progress(f"[stage 5/5] C1 review done ({_elapsed(stage_start)})")

    briefing_md = build_daily_briefing(
        date,
        news_dict,
        errors,
        retrieve_result,
        review_copies=review_copies,
    )
    briefing_path.parent.mkdir(parents=True, exist_ok=True)
    briefing_path.write_text(briefing_md, encoding="utf-8")

    candidates_path = briefing_path.parent / f"{date}_candidates.json"
    candidates_path.write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {briefing_path.resolve()}", file=sys.stderr)
    print(f"Wrote {candidates_path.resolve()}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the daily briefing pipeline: news → agents → retrieve → Daily_Briefing.md.",
    )
    news_group = parser.add_mutually_exclusive_group()
    news_group.add_argument("--news-file", help="Path to news JSON (title/description required).")
    news_group.add_argument("--url", help="Single article URL; requires --title/--description fallback.")
    news_group.add_argument("--pick", type=int, metavar="N", help="1-based Guardian API candidate to select.")
    parser.add_argument("--title", help="Fallback title for --url.")
    parser.add_argument("--description", help="Fallback description for --url.")
    parser.add_argument("--date", help="Briefing date override (default: today, UTC, YYYY-MM-DD).")
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    parser.add_argument("--no-copy", action="store_true", help="Skip C1 (compose.run_review); debug use.")
    parser.add_argument(
        "--personas",
        type=int,
        default=None,
        metavar="N",
        help="Dev shortcut: only run the first N personas (default: all 12).",
    )
    parser.add_argument(
        "--skip-expand",
        action="store_true",
        help="Dev shortcut: skip the P-Expand stage.",
    )
    parser.add_argument(
        "--judge-topk",
        type=int,
        default=2,
        metavar="K",
        help="Retrieve top-k per pseudo (default: 2).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing same-date briefing instead of erroring out.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        build_parser().print_usage(sys.stderr)
        return 2

    # main.py has no top-level argparse subparsers (existing CLI style predates
    # this todo); dispatch "publish" as a lightweight sub-command by peeling
    # off argv[0] before the daily-pipeline parser ever sees it.
    if argv[0] == "publish":
        publish_parser = build_publish_parser()
        publish_args = publish_parser.parse_args(argv[1:])
        try:
            return _run_publish_cli(publish_args)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        except KeyboardInterrupt:
            print("interrupted", file=sys.stderr)
            return 130

    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.news_file and not args.url and args.pick is None:
        parser.print_usage(sys.stderr)
        print("error: one of --news-file / --url / --pick is required", file=sys.stderr)
        return 2

    try:
        return asyncio.run(_run_cli(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())