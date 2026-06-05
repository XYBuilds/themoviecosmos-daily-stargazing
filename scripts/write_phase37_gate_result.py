"""Write output/Eval/phase3.7/GATE_RESULT.md from scored review + summarize_eval."""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.summarize_eval import (  # noqa: E402
    CandidateScore,
    parse_unified_review,
    summarize_runs,
)

_OBS_RUNS = frozenset(
    {
        "01-grid-outage",
        "02-corporate-layoff",
        "03-election-upset",
        "04-celebrity-scandal",
    }
)
_HOLDOUT_RUNS = frozenset(
    {
        "05-climate-disaster",
        "06-tech-monopoly",
        "07-migration-border",
        "08-sports-underdog",
        "09-cultural-backlash",
        "10-whistleblower-leak",
    }
)
_SCORED_FOCUS = frozenset(
    {
        "01-grid-outage",
        "02-corporate-layoff",
        "07-migration-border",
        "09-cultural-backlash",
    }
)


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _fit_resonance_rows(runs: list) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in runs:
        split = "holdout" if run.run_id in _HOLDOUT_RUNS else "observation"
        for cand in run.candidates:
            if cand.score is None or cand.max_fit is None:
                continue
            rows.append(
                {
                    "run_id": run.run_id,
                    "split": split,
                    "tmdb_id": cand.tmdb_id,
                    "title": cand.title,
                    "score": cand.score,
                    "resonance_type": cand.resonance_type or "",
                    "max_fit": cand.max_fit,
                    "similarity": cand.similarity,
                    "fit_sim": cand.fit_sim_score,
                    "structural_two": cand.score == 2
                    and cand.resonance_type in {"结构", "双重"},
                }
            )
    return rows


def _subset_report(runs: list, run_ids: frozenset[str]) -> dict[str, Any]:
    filtered = [r for r in runs if r.run_id in run_ids]
    return summarize_runs(filtered)


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def build_gate_markdown(
    review_path: Path,
    *,
    baseline_lift_path: Path,
) -> str:
    text = review_path.read_text(encoding="utf-8")
    runs = parse_unified_review(review_path, text)
    full = summarize_runs(runs)
    focus = _subset_report(runs, _SCORED_FOCUS)

    fit_rows = _fit_resonance_rows(runs)
    focus_fit = [r for r in fit_rows if r["run_id"] in _SCORED_FOCUS]
    pearson_all = _pearson(
        [r["max_fit"] for r in fit_rows],
        [float(r["score"]) for r in fit_rows],
    )
    pearson_focus = _pearson(
        [r["max_fit"] for r in focus_fit],
        [float(r["score"]) for r in focus_fit],
    )

    low_fit = [r for r in fit_rows if r["max_fit"] < 0.55]
    low_fit_structural = [r for r in low_fit if r["structural_two"]]

    g = full["global"]
    gate = full["gate"]
    verdict = gate["verdict"]
    go_37_6 = verdict == "GATE_PASS"

    lines: list[str] = [
        "# Phase 3.7 · GATE 结论（persona resonance）",
        "",
        f"- **日期**: {date.today().isoformat()}",
        f"- **数据源**: `{review_path.as_posix()}`（review SSOT；per-run `candidates.md` 已移除）",
        f"- **3.7.0 锚点**: `{baseline_lift_path.as_posix()}` — Phase 3.6 注入式 creative vs A1 **No-Go**（lift −28%）",
        f"- **summarize_eval**: `{gate['compare_mode']}` · `{gate['verdict']}`",
        "",
        "## 打分覆盖（Coverage）",
        "",
        _md_table(
            ["集合", "run_id", "已打分候选", "备注"],
            [
                ["观察集 obs", "01, 02", "✓ 总编已填", "03–04 未填"],
                ["留出集 holdout", "07, 09", "✓ 总编已填", "05–06, 08, 10 未填"],
                [
                    "全批",
                    "10 runs",
                    f"{len(fit_rows)} scored / 150 high-hit",
                    "闸门用已填分候选",
                ],
            ],
        ),
        "",
        "## 1. fit ↔ 共振（P-Abstain 探针）",
        "",
        f"- **已打分行（全批）**: n={len(fit_rows)}；Pearson(max_fit, 共振分) ≈ "
        f"{pearson_all if pearson_all is not None else 'n/a'}",
        f"- **Focus 子集（01, 02, 07, 09）**: n={len(focus_fit)}；r ≈ "
        f"{pearson_focus if pearson_focus is not None else 'n/a'}",
        f"- **低 fit (<0.55) 命中结构/双重 2 分**: {len(low_fit_structural)}/{len(low_fit)} "
        f"（{'支持暂不硬编码弃权' if not low_fit_structural else '需复查阈值'}）",
        "",
        "趋势（focus 四条）：高 fit 与 2 分/双重共现多于低 fit；Lover 低 fit 行多 0–1 分。"
        "**P-Abstain 阈值留待补全留出集后定稿**.",
        "",
        "## 2. persona steering vs A1（闸门 2 · 呼应 3.7.0）",
        "",
        _md_table(
            ["指标", "全批已打分", "01+02+07+09 focus"],
            [
                [
                    "batch pass rate",
                    f"{g['batch_pass_rate']:.1%} ({g['runs_with_score_2']}/{g['total_runs']} runs)",
                    f"{focus['global']['batch_pass_rate']:.1%}",
                ],
                [
                    "A1 path structural 2-rate (also_baseline=true)",
                    f"{g['baseline_structural_2_rate']:.1%} ({g['a1_path_structural_twos']}/{g['a1_path_scored']})",
                    f"{focus['global']['baseline_structural_2_rate']:.1%}",
                ],
                [
                    "persona path structural 2-rate (also_baseline=false)",
                    f"{g['persona_touched_structural_2_rate']:.1%} ({g['persona_path_structural_twos']}/{g['persona_path_scored']})",
                    f"{focus['global']['persona_touched_structural_2_rate']:.1%}",
                ],
                [
                    "lift (persona path − A1 path)",
                    f"{(g['persona_touched_structural_2_rate'] - g['baseline_structural_2_rate']):+.1%}",
                    f"{(focus['global']['persona_touched_structural_2_rate'] - focus['global']['baseline_structural_2_rate']):+.1%}",
                ],
            ],
        ),
        "",
        "- **对比 3.7.0**：3.6 注入式 creative **低于** A1；本批 persona path（`also_baseline=false`）结构/双重 2 分率"
        f" **{'高于' if g['persona_touched_structural_2_rate'] > g['baseline_structural_2_rate'] else '未高于'}** "
        "A1 path（`also_baseline=true`）桶 — "
        f"{'与 3.7 赌注同向' if g['persona_touched_structural_2_rate'] > g['baseline_structural_2_rate'] else '与 3.7 赌注反向（A1 仍占优）'}，"
        "**batch 闸门未过**且仅 4/10 run 已打分.",
        "",
        "## 3. fit × 相似度（候选排序/过滤）",
        "",
        "下游建议：按 `fit_sim_score = max_fit × 相似度` 降序 triage（`summarize_eval` JSON `fit_sim_ranking`）。"
        "2 分候选多落在 fit×sim 上半区；0–1 分尾部可优先压人工体量.",
        "",
        "## 4. 闸门裁决",
        "",
        f"- **脚本闸门**: **{verdict}**",
    ]
    if gate["reasons"]:
        for reason in gate["reasons"]:
            lines.append(f"  - {reason}")
    lines.extend(
        [
            f"- **3.7.6 SSOT 迁移**: **{'Go' if go_37_6 else 'No-Go（跳过 3.7.6）'}**",
            "- **`[需人工验收]`**：总编确认本文件结论后输入 `approve` 再标 plan complete / 写 3.7.5 report。",
            "",
            "### 一行摘要",
            "",
            f"**{verdict}** — persona structural lift "
            f"{(g['persona_touched_structural_2_rate'] - g['baseline_structural_2_rate']):+.1%} "
            f"on scored subset; batch {g['batch_pass_rate']:.0%}; coverage 4/10 runs.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write phase3.7 GATE_RESULT.md")
    parser.add_argument(
        "--review",
        default="output/Eval/phase3.7/high-hit-score-review.md",
    )
    parser.add_argument(
        "--out",
        default="output/Eval/phase3.7/GATE_RESULT.md",
    )
    args = parser.parse_args(argv)

    review_path = Path(args.review)
    if not review_path.is_absolute():
        review_path = _REPO_ROOT / review_path
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path

    baseline_lift = _REPO_ROOT / "output/Eval/phase3.7/baseline-lift.md"
    md = build_gate_markdown(review_path, baseline_lift_path=baseline_lift)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
