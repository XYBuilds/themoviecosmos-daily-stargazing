"""Phase 3.12.6 离线等价性验证.

把 3.11.7 全批基线的 agents.json（含 search_units dict）喂给重构后的
retrieve.from_agents_json，逐条对比候选 tmdb_id 集合、search_unit_kind 分解、
守卫硬失败，与基线 retrieve.json 比对。

纯重构（仅删除 channel 诊断字段）下召回是确定性的，候选集应 bit-parity。

用法:
    python -m scripts.verify_phase312_equivalence \
        --baseline-dir output/Eval/phase3.11/full-batch-20260613-3117 \
        --out output/Eval/phase3.12/equivalence-report.json
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

from scripts.retrieve import (  # noqa: E402
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_QUALITY_FLOOR,
    DEFAULT_TOP_K,
    from_agents_json,
)


def _candidate_ids(payload: dict[str, Any]) -> list[int]:
    out: list[int] = []
    for row in payload.get("candidates", []):
        if isinstance(row, dict) and row.get("tmdb_id") is not None:
            out.append(int(row["tmdb_id"]))
    return out


def _kind_breakdown(payload: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for agent in payload.get("per_agent", []):
        if not isinstance(agent, dict):
            continue
        for pseudo in agent.get("pseudos", []):
            source = pseudo.get("source") if isinstance(pseudo, dict) else None
            source = source if isinstance(source, dict) else {}
            kind = str(source.get("search_unit_kind") or "").strip().lower()
            if kind:
                counts[kind] = counts.get(kind, 0) + 1
    return counts


def _a1_oracle_ids(payload: dict[str, Any]) -> list[int]:
    oracle = payload.get("a1_oracle")
    if not isinstance(oracle, dict):
        return []
    ids = oracle.get("hit_tmdb_ids")
    if isinstance(ids, list):
        return sorted(int(x) for x in ids)
    return []


def _compare_one(news_dir: Path) -> dict[str, Any]:
    agents_path = news_dir / "agents.json"
    baseline_path = news_dir / "retrieve.json"

    replay = from_agents_json(
        agents_path,
        top_k=DEFAULT_TOP_K,
        max_candidates=DEFAULT_MAX_CANDIDATES,
        quality_floor=DEFAULT_QUALITY_FLOOR,
    )
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))

    replay_ids = _candidate_ids(replay)
    baseline_ids = _candidate_ids(baseline)
    replay_set = set(replay_ids)
    baseline_set = set(baseline_ids)

    replay_kinds = _kind_breakdown(replay)
    baseline_kinds = _kind_breakdown(baseline)

    replay_oracle = _a1_oracle_ids(replay)
    baseline_oracle = _a1_oracle_ids(baseline)

    return {
        "news": news_dir.name,
        "candidate_set_equal": replay_set == baseline_set,
        "candidate_order_equal": replay_ids == baseline_ids,
        "baseline_only": sorted(baseline_set - replay_set),
        "replay_only": sorted(replay_set - baseline_set),
        "baseline_count": len(baseline_ids),
        "replay_count": len(replay_ids),
        "kind_breakdown_equal": replay_kinds == baseline_kinds,
        "baseline_kinds": baseline_kinds,
        "replay_kinds": replay_kinds,
        "a1_oracle_equal": replay_oracle == baseline_oracle,
        "baseline_oracle": baseline_oracle,
        "replay_oracle": replay_oracle,
    }


def run(baseline_dir: Path) -> dict[str, Any]:
    news_dirs = sorted(
        d for d in baseline_dir.iterdir() if d.is_dir() and (d / "agents.json").is_file()
    )
    per_news = [_compare_one(d) for d in news_dirs]

    set_mismatches = [r for r in per_news if not r["candidate_set_equal"]]
    order_mismatches = [r for r in per_news if not r["candidate_order_equal"]]
    kind_mismatches = [r for r in per_news if not r["kind_breakdown_equal"]]
    oracle_mismatches = [r for r in per_news if not r["a1_oracle_equal"]]

    return {
        "baseline_dir": str(baseline_dir),
        "news_count": len(per_news),
        "summary": {
            "candidate_set_bit_parity": not set_mismatches,
            "candidate_order_bit_parity": not order_mismatches,
            "kind_breakdown_parity": not kind_mismatches,
            "a1_oracle_parity": not oracle_mismatches,
            "set_mismatch_news": [r["news"] for r in set_mismatches],
            "order_mismatch_news": [r["news"] for r in order_mismatches],
            "kind_mismatch_news": [r["news"] for r in kind_mismatches],
            "oracle_mismatch_news": [r["news"] for r in oracle_mismatches],
        },
        "per_news": per_news,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3.12.6 离线等价性验证")
    parser.add_argument(
        "--baseline-dir",
        default="output/Eval/phase3.11/full-batch-20260613-3117",
        help="3.11.7 全批基线目录（含每条新闻 agents.json + retrieve.json）",
    )
    parser.add_argument("--out", default=None, help="报告 JSON 输出路径")
    args = parser.parse_args(argv)

    baseline_dir = Path(args.baseline_dir)
    if not baseline_dir.is_absolute():
        baseline_dir = _REPO_ROOT / baseline_dir
    if not baseline_dir.is_dir():
        print(f"error: baseline dir not found: {baseline_dir}", file=sys.stderr)
        return 2

    report = run(baseline_dir)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = _REPO_ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
        print(f"Wrote {out.resolve()}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(serialized.encode("utf-8"))

    s = report["summary"]
    all_parity = (
        s["candidate_set_bit_parity"]
        and s["kind_breakdown_parity"]
        and s["a1_oracle_parity"]
    )
    print(
        "EQUIVALENCE: "
        + ("PASS" if all_parity else "DIVERGENT")
        + f" (set={s['candidate_set_bit_parity']} "
        + f"order={s['candidate_order_bit_parity']} "
        + f"kind={s['kind_breakdown_parity']} "
        + f"oracle={s['a1_oracle_parity']})",
        file=sys.stderr,
    )
    return 0 if all_parity else 1


if __name__ == "__main__":
    raise SystemExit(main())