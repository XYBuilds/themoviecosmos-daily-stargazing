"""Apply obs 01–04 fresh human labels under Phase 3.10 dual-axis rubric.

Phase 3.10.5: scores observation-set candidates in ``high-hit-score-review.md``
without referencing phase3.9 or earlier human scores. Writes
``obs-fresh-labels.json`` audit trail.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.llm_judge import (
    JudgeItem,
    _TMDB_LINE,
    build_judge_user_prompt,
    collect_judge_items,
    parse_judge_response,
)

_SCORE_LINE = re.compile(r"^(-\s*\*\*共振分\*\*:)(.*)$", re.MULTILINE)
_TYPE_LINE = re.compile(r"^(-\s*\*\*共振类型\*\*:)(.*)$", re.MULTILINE)
from scripts.resonance_rubric import TYPE_NONE, validate_score_type_pair
from scripts.run_persona_batch import OBS_RUN_PREFIXES

PHASE310 = _REPO_ROOT / "output" / "Eval" / "phase3.10"
_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:)(.*)$", re.MULTILINE)
_HEADING = re.compile(r"^###\s+.+$", re.MULTILINE)
_RUN_ID_COMMENT = re.compile(r"<!--\s*run_id:\s*(\S+)\s*-->")

_EDITOR_SYSTEM = (
    "You are the chief editor (总编) for a news-to-film resonance eval. "
    "Score each pair using the Phase 3.10 dual-axis rubric ONLY: "
    "(1) surface element — concrete load-bearing anchor with 0-guard; "
    "(2) underlying logic — same causal-stakes engine invariant under POV/scale, "
    "gated by a falsifiable 'X under constraint Z drives Y' sentence for BOTH sides. "
    "Abstract power-role pairings are NOT surface elements. "
    "Return only valid JSON. Do not reference or infer any prior human scores."
)

_V2_RUBRIC_HEADER = """\
### 共振分 Rubric（2×2 · Phase 3.10 双轴 · SSOT `docs/eval-the-bet.md` §4）

先判 **承重表层元素**（有/无），再判 **POV/尺度不变因果引擎**（是/否）+ **因果反测句**：

| 表层元素 | 底层逻辑 | 分  | 共振类型                       |
| -------- | -------- | --- | ------------------------------ |
| 无       | 否       | 0   | （留空）无共振（偶然词面重叠） |
| 无       | 是       | 1   | 深层共振（仅逻辑，无表层）     |
| 有       | 否       | 1   | 表层沾边                       |
| 有       | 是       | 2   | 强共振（表层 + 逻辑）          |

总编与 LLM judge 均输出 `共振分` + `共振类型`，须与上表一致。
"""


@dataclass
class FreshLabel:
    run_id: str
    tmdb_id: str
    title: str
    score: int
    resonance_type: str | None
    causal_test: str
    labeled_at: str
    rationale: str = ""
    remark: str = ""
    source: str = "llm"


def _obs_run_ids(run_ids: list[str] | None) -> list[str]:
    if run_ids:
        return [r for r in run_ids if r.startswith(OBS_RUN_PREFIXES)]
    return [r for r in ("01-grid-outage", "02-corporate-layoff", "03-election-upset", "04-celebrity-scandal")]


def call_editor_label(
    item: JudgeItem,
    *,
    provider: str | None = None,
    client=None,
    max_retries: int = 3,
) -> tuple[int, str | None, str, str]:  # score, type, rationale, causal_test
    load_env()
    prov = (provider or default_llm_provider()).strip().lower()
    llm = client or get_llm_client(prov)
    import os

    model_env = "MIMO_MODEL" if prov == "mimo" else "DEEPSEEK_MODEL"
    model = os.getenv(model_env, "").strip()
    if not model:
        raise RuntimeError(f"Missing {model_env} for provider {prov!r}")

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = llm.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _EDITOR_SYSTEM},
                    {"role": "user", "content": build_judge_user_prompt(item)},
                ],
                temperature=0.2,
            )
            content = (response.choices[0].message.content or "").strip()
            score, resonance_type, rationale, causal_test = parse_judge_response(content)
            return score, resonance_type, rationale, causal_test
        except Exception as exc:
            last_err = exc
            if attempt + 1 < max_retries:
                time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(
        f"editor label failed for {item.run_id}/{item.tmdb_id}: {last_err}"
    ) from last_err


def _update_rubric_header(text: str) -> str:
    old = re.compile(
        r"### 共振分 Rubric.*?(?=### Per-news|\n## \d{2}-|\Z)",
        re.DOTALL,
    )
    if old.search(text):
        return old.sub(_V2_RUBRIC_HEADER + "\n", text, count=1)
    return text


def _apply_labels_to_review(
    text: str,
    labels: dict[tuple[str, str], FreshLabel],
    *,
    human_fields: bool = False,
) -> str:
    """Patch review human editor fields from audit labels.

    When ``human_fields`` is False (default), human fields are left unchanged so
    LLM output stays in audit JSON / judge fields only.
    """
    if not human_fields:
        return text
    section_re = re.compile(r"^(## \d{2}-[^\n]+)$", re.MULTILINE)
    matches = list(section_re.finditer(text))
    if not matches:
        return text

    out: list[str] = []
    cursor = 0
    for i, match in enumerate(matches):
        out.append(text[cursor : match.start()])
        section_start = match.start()
        section_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[section_start:section_end]
        run_id = match.group(1).removeprefix("## ").strip()

        def _patch_block(block: str) -> str:
            tmdb_match = _TMDB_LINE.search(block)
            if not tmdb_match:
                return block
            label = labels.get((run_id, tmdb_match.group(1)))
            if not label:
                return block
            score_str = str(label.score)
            type_str = label.resonance_type or ""
            block, _ = _SCORE_LINE.subn(
                rf"\1 {score_str}  <!-- 总编填写 0 / 1 / 2 -->",
                block,
                count=1,
            )
            block, _ = _TYPE_LINE.subn(
                rf"\1 {type_str}  <!-- 0 留空；1→深层共振（仅逻辑，无表层）|表层沾边；2→强共振（表层 + 逻辑） -->",
                block,
                count=1,
            )
            if label.remark.strip():
                block = _REMARK_LINE.sub(rf"\1 {label.remark}", block, count=1)
            return block

        blocks = re.split(r"(?=^###\s+)", section, flags=re.MULTILINE)
        patched = [_patch_block(b) if b.startswith("###") else b for b in blocks]
        out.append("".join(patched))
        cursor = section_end
    out.append(text[cursor:])
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=PHASE310,
        help="Phase 3.10 eval directory",
    )
    parser.add_argument(
        "--run-ids",
        nargs="*",
        help="Observation run ids (default: 01–04)",
    )
    parser.add_argument("--provider", default=None)
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between LLM calls")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--apply-only",
        action="store_true",
        help="Patch high-hit-score-review.md from existing obs-fresh-labels.json",
    )
    parser.add_argument(
        "--human",
        action="store_true",
        help="Write scores/types (and optional human remark) to editor fields in review",
    )
    args = parser.parse_args(argv)

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    review_path = eval_dir / "high-hit-score-review.md"
    if not review_path.is_file():
        print(f"missing review: {review_path}", file=sys.stderr)
        return 1

    audit_path = eval_dir / "obs-fresh-labels.json"
    obs_ids = _obs_run_ids(args.run_ids)

    if args.apply_only:
        if not audit_path.is_file():
            print(f"missing audit: {audit_path}", file=sys.stderr)
            return 1
        prior = json.loads(audit_path.read_text(encoding="utf-8"))
        labels = {
            (row["run_id"], str(row["tmdb_id"])): FreshLabel(**row)
            for row in prior.get("labels") or []
        }
        review_text = review_path.read_text(encoding="utf-8")
        review_text = _update_rubric_header(review_text)
        review_path.write_text(
            _apply_labels_to_review(review_text, labels, human_fields=args.human),
            encoding="utf-8",
        )
        mode = "human editor fields" if args.human else "no human fields (audit only)"
        print(f"applied {len(labels)} labels to {review_path} ({mode})")
        return 0

    items = collect_judge_items(eval_dir, review_path=review_path, run_ids=obs_ids)
    # Strip any inherited human scores — fresh label only
    for item in items:
        item.human_score = None
        item.human_resonance_type = None

    if not items:
        print("no obs candidates found", file=sys.stderr)
        return 1

    print(f"labeling {len(items)} obs candidates across {obs_ids}", file=sys.stderr)

    labels: dict[tuple[str, str], FreshLabel] = {}
    if audit_path.is_file():
        prior = json.loads(audit_path.read_text(encoding="utf-8"))
        for row in prior.get("labels") or []:
            key = (row["run_id"], str(row["tmdb_id"]))
            labels[key] = FreshLabel(**row)

    for i, item in enumerate(items):
        key = (item.run_id, item.tmdb_id)
        if key in labels:
            print(f"  [{i + 1}/{len(items)}] skip (cached) {item.run_id} · {item.title}", file=sys.stderr)
            continue
        print(f"  [{i + 1}/{len(items)}] {item.run_id} · {item.title}", file=sys.stderr)
        if args.dry_run:
            continue
        score, rtype, rationale, causal_test = call_editor_label(
            item, provider=args.provider
        )
        validate_score_type_pair(score, rtype)
        labels[key] = FreshLabel(
            run_id=item.run_id,
            tmdb_id=item.tmdb_id,
            title=item.title,
            score=score,
            resonance_type=rtype,
            causal_test=causal_test,
            rationale=rationale,
            labeled_at=datetime.now(UTC).isoformat(),
            source="llm",
        )
        audit = {
            "eval_phase": "3.10",
            "rubric": "dual-axis v2 (docs/eval-the-bet.md §4)",
            "observation_run_ids": obs_ids,
            "labeled_at": datetime.now(UTC).isoformat(),
            "count": len(labels),
            "labels": [asdict(v) for v in labels.values()],
        }
        audit_path.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if args.delay > 0 and i + 1 < len(items):
            time.sleep(args.delay)

    if args.dry_run:
        print("dry-run complete", file=sys.stderr)
        return 0

    audit = {
        "eval_phase": "3.10",
        "rubric": "dual-axis v2 (docs/eval-the-bet.md §4)",
        "observation_run_ids": obs_ids,
        "labeled_at": datetime.now(UTC).isoformat(),
        "count": len(labels),
        "labels": [asdict(v) for v in labels.values()],
    }
    review_text = review_path.read_text(encoding="utf-8")
    review_text = _update_rubric_header(review_text)
    if args.human:
        review_text = _apply_labels_to_review(review_text, labels, human_fields=True)
        review_path.write_text(review_text, encoding="utf-8")

    # Verification: no missing labels in obs sections
    missing = []
    for item in items:
        key = (item.run_id, item.tmdb_id)
        if key not in labels:
            missing.append(key)
    if missing:
        print(f"ERROR: {len(missing)} missing labels", file=sys.stderr)
        return 1

    scored_in_review = 0
    for rid in obs_ids:
        section = re.search(rf"^## {re.escape(rid)}\s", review_text, re.M)
        if not section:
            continue
        start = section.start()
        nxt = re.search(r"^## \d{2}-", review_text[section.end() :], re.M)
        end = section.end() + nxt.start() if nxt else len(review_text)
        chunk = review_text[start:end]
        scored_in_review += len(re.findall(r"- \*\*共振分\*\*: [012]", chunk))

    print(f"wrote {audit_path} ({len(labels)} labels)")
    print(f"obs review blocks with scores: {scored_in_review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
