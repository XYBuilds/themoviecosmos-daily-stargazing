"""build_data.py · Phase 8.1 · 每日审核面板数据聚合瘦身.

从 output/daily_batch/{date}/{NN}-{slug}/ 下的 news.json / retrieve.json /
llm-judge-scores.json 聚合出前端只读的 panel.json（瘦身：只保留展示所需字段）。

关键点：
- retrieve.json 里 candidate.tmdb_id 是 int，llm-judge-scores.json 里 scores[].tmdb_id
  是 str，两者来源不同管线（retrieve 走 TMDB API，judge 走 LLM 结构化输出），join 前
  必须统一 str() 归一化，否则永远 join 不上。
- judge 分数文件整体缺失，或某个 tmdb_id 未被 judge 覆盖（judge 只对候选做抽样评分），
  都是正常业务状态而非异常，因此容错为空值而不抛异常。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.lib.paths import repo_root  # noqa: E402


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_index(slug: str, fallback: int) -> int:
    prefix = slug.split("-", 1)[0]
    # 目录序号前缀解析失败时退回枚举序，保证 index 字段始终可用而不是让整条流程失败。
    return int(prefix) if prefix.isdigit() else fallback


def _extract_resonance_agents(hit_sources: list[dict]) -> list[str]:
    """从 hit_sources 提取去重后的共振 agent_id 列表，保持首次出现顺序。"""
    seen: set[str] = set()
    agents: list[str] = []
    for hit in hit_sources:
        agent_id = hit.get("agent_id")
        if agent_id is None or agent_id in seen:
            continue
        seen.add(agent_id)
        agents.append(agent_id)
    return agents


def _judge_index_by_tmdb_id(judge_scores: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for entry in judge_scores.get("scores", []):
        # str() 归一化：judge scores 的 tmdb_id 是字符串，candidate 的是 int。
        key = str(entry.get("tmdb_id"))
        index[key] = entry
    return index


def _join_judge_scores(candidates: list[dict], judge_scores: dict) -> list[dict]:
    """按 tmdb_id（str 归一化）把 judge 的评分字段 join 进瘦身后的 candidates。"""
    judge_by_id = _judge_index_by_tmdb_id(judge_scores)
    joined: list[dict] = []
    for candidate in candidates:
        judge_entry = judge_by_id.get(str(candidate.get("tmdb_id")), {})
        joined.append(
            {
                "tmdb_id": candidate.get("tmdb_id"),
                "title": candidate.get("title"),
                "release_year": candidate.get("release_year"),
                "overview": candidate.get("overview"),
                "genres": candidate.get("genres"),
                "language": candidate.get("language"),
                "similarity": candidate.get("similarity"),
                "movie_url": candidate.get("movie_url"),
                "poster_path": candidate.get("poster_path"),
                "resonance_agents": _extract_resonance_agents(
                    candidate.get("hit_sources", [])
                ),
                "judge_score": judge_entry.get("judge_score"),
                "judge_resonance_type": judge_entry.get("judge_resonance_type"),
                "judge_rationale": judge_entry.get("rationale"),
                "causal_test": judge_entry.get("causal_test"),
            }
        )
    return joined


def _load_judge_scores(news_dir: Path) -> dict:
    judge_path = news_dir / "llm-judge-scores.json"
    # judge 文件缺失是正常状态（未跑 judge 阶段的日批），不是错误。
    if not judge_path.is_file():
        return {}
    return _read_json(judge_path)


def _build_news_item(news_dir: Path, fallback_index: int) -> dict | None:
    news_path = news_dir / "news.json"
    if not news_path.is_file():
        return None

    news = _read_json(news_path)
    retrieve = _read_json(news_dir / "retrieve.json")
    judge_scores = _load_judge_scores(news_dir)

    return {
        "index": _parse_index(news_dir.name, fallback_index),
        "slug": news_dir.name,
        "news": {
            "title": news.get("title"),
            "description": news.get("description"),
            "source_name": news.get("source_name"),
            "pub_time": news.get("pub_time"),
            "url": news.get("url"),
        },
        "candidates": _join_judge_scores(
            retrieve.get("candidates", []), judge_scores
        ),
    }


def build_panel_data(date: str, batch_root: Path | None = None) -> dict:
    """聚合返回 panel dict（结构见 panel.json schema）。"""
    root = batch_root or _default_batch_root()
    date_dir = root / date

    news_dirs = sorted(
        (p for p in date_dir.iterdir() if p.is_dir() and (p / "news.json").is_file()),
        key=lambda p: p.name,
    )

    news_items = []
    for fallback_index, news_dir in enumerate(news_dirs, start=1):
        item = _build_news_item(news_dir, fallback_index)
        if item is not None:
            news_items.append(item)
    news_items.sort(key=lambda item: item["index"])

    return {
        "date": date,
        "generated_at": datetime.now(UTC).isoformat(),
        "news_items": news_items,
    }


def write_panel_json(date: str, batch_root: Path | None = None) -> Path:
    """调 build_panel_data 并写 output/daily_batch/{date}/panel.json，返回路径。"""
    root = batch_root or _default_batch_root()
    panel = build_panel_data(date, batch_root=root)
    panel_path = root / date / "panel.json"
    panel_path.write_text(
        json.dumps(panel, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return panel_path


def list_available_dates(batch_root: Path | None = None) -> list[str]:
    """扫描 output/daily_batch/*/ 提取日期目录名，倒序返回。"""
    root = batch_root or _default_batch_root()
    if not root.is_dir():
        return []
    dates = [p.name for p in root.iterdir() if p.is_dir()]
    return sorted(dates, reverse=True)


def _run_cli() -> int:
    parser = argparse.ArgumentParser(description="Build review panel data from a daily_batch date directory.")
    parser.add_argument("--date", required=True, help="日期，如 2026-07-06")
    parser.add_argument("--batch-root", type=Path, default=None, help="覆盖默认 output/daily_batch 根目录")
    parser.add_argument("--dry-run", action="store_true", help="只 build 不写 panel.json，打印新闻数与候选数")
    args = parser.parse_args()

    if args.dry_run:
        panel = build_panel_data(args.date, batch_root=args.batch_root)
        candidate_count = sum(len(item["candidates"]) for item in panel["news_items"])
        print(f"news_items={len(panel['news_items'])} candidates={candidate_count}")
        return 0

    panel_path = write_panel_json(args.date, batch_root=args.batch_root)
    print(panel_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())