from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"t:\themoviecosmos-daily-stargazing")
REVIEW = ROOT / "output" / "Eval" / "phase3.11" / "full-batch-20260613-3117" / "high-hit-score-review.md"
THINKING = ROOT / "output" / "Eval" / "phase3.11" / "full-batch-20260613-3117" / "llm-judge-scores-thinking-enabled.json"

review_text = REVIEW.read_text(encoding="utf-8")
payload = json.loads(THINKING.read_text(encoding="utf-8"))
calibration = payload.get("calibration") or {}
metadata = payload.get("run_metadata") or {}
scores = {
    (str(row.get("run_id")), str(row.get("tmdb_id"))): row
    for row in payload.get("scores") or []
}

if len(scores) != 110:
    raise SystemExit(f"thinking score count must be 110, got {len(scores)}")

trust_status = str(calibration.get("trust_status") or "不采信")
screening_only = bool(calibration.get("screening_only"))
prompt_version = str(payload.get("prompt_version") or "")
provider = str(metadata.get("provider") or "")
thinking_mode = str(metadata.get("thinking_mode") or "")
condition_note = str(metadata.get("judge_condition_note") or "")

header_lines = [
    f"- **LLM judge thinking-enabled:** `llm-judge-scores-thinking-enabled.json` — trust_status={trust_status}"
    + (" (screening only; separate LLM Judge thinking block per candidate)" if screening_only else " (separate LLM Judge thinking block per candidate)"),
    f"- **LLM judge thinking prompt_version:** `{prompt_version}`",
    f"- **LLM judge thinking provider:** `{provider}`",
    f"- **LLM judge thinking_mode:** `{thinking_mode}`",
    f"- **LLM judge thinking condition note:** {condition_note}",
]

# Make header update idempotent.
lines = review_text.splitlines()
lines = [line for line in lines if not line.startswith("- **LLM judge thinking")]
insert_after = None
for idx, line in enumerate(lines):
    if line.startswith("- **LLM judge condition note:**"):
        insert_after = idx
        break
if insert_after is None:
    for idx, line in enumerate(lines):
        if line.strip() == "### Sources":
            insert_after = idx
            break
if insert_after is None:
    raise SystemExit("Could not locate Sources header insertion point")
lines[insert_after + 1:insert_after + 1] = header_lines
review_text = "\n".join(lines) + "\n"

RUN_ID_COMMENT = re.compile(r"^<!-- run_id: (\S+) -->", re.MULTILINE)
TMDB_LINE = re.compile(r"^- \*\*tmdb_id\*\*: (\S+)", re.MULTILINE)
SCORING_REMARK_LINE = re.compile(r"^(- \*\*打分备注\*\*:.*)$", re.MULTILINE)
REGULAR_JUDGE_BLOCK = re.compile(r"(- \*\*LLM Judge（自动评审）\*\*:\n(?:  - \*\*judge[^\n]*\n)*)")
THINKING_JUDGE_BLOCK = re.compile(r"\n?- \*\*LLM Judge（thinking 自动评审）\*\*:\n(?:  - \*\*thinking judge[^\n]*\n?)*", re.MULTILINE)


def thinking_lines(row: dict) -> list[str]:
    lines = [
        "- **LLM Judge（thinking 自动评审）**:",
        f"  - **thinking judge分**: {row.get('judge_score')}",
        f"  - **thinking judge共振类型**: {row.get('judge_resonance_type') or ''}",
    ]
    if row.get("judge_pov_transform"):
        lines.append("  - **thinking judge POV变换**: 是")
    if row.get("disagreement"):
        lines.append("  - **thinking judge分歧**: ⚠")
    if screening_only or trust_status != "采信":
        lines.append(f"  - **thinking judge采信**: {trust_status} · screening only")
    else:
        lines.append(f"  - **thinking judge采信**: {trust_status}")
    causal_test = str(row.get("causal_test") or "").strip()
    rationale = str(row.get("rationale") or "").strip()
    if causal_test:
        lines.append(f"  - **thinking judge因果反测**: {causal_test}")
    if rationale:
        lines.append(f"  - **thinking judge理由**: {rationale}")
    return lines


def strip_existing_thinking(block: str) -> str:
    stripped = THINKING_JUDGE_BLOCK.sub("\n", block)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped.rstrip()) + "\n"
    return stripped


def insert_thinking_block(block: str, row: dict) -> str:
    insert = "\n".join(thinking_lines(row)) + "\n"
    block = strip_existing_thinking(block)
    match = REGULAR_JUDGE_BLOCK.search(block)
    if match:
        return REGULAR_JUDGE_BLOCK.sub(lambda m: m.group(1).rstrip() + "\n" + insert, block, count=1)
    if SCORING_REMARK_LINE.search(block):
        return SCORING_REMARK_LINE.sub(lambda m: f"{m.group(1)}\n{insert.rstrip()}", block, count=1)
    return block.rstrip() + "\n" + insert

chunks = re.split(r"(?=<!-- run_id: )", review_text)
out_parts: list[str] = [chunks[0]]
patched_count = 0
for chunk in chunks[1:]:
    run_match = RUN_ID_COMMENT.match(chunk)
    run_id = run_match.group(1) if run_match else ""
    heading_parts = re.split(r"(?=^### )", chunk, flags=re.MULTILINE)
    patched_chunk = heading_parts[0]
    for part in heading_parts[1:]:
        tmdb_match = TMDB_LINE.search(part)
        if tmdb_match and run_id:
            row = scores.get((run_id, tmdb_match.group(1)))
            if row is not None:
                part = insert_thinking_block(part, row)
                patched_count += 1
        if part and not part.endswith("\n\n"):
            part = part.rstrip() + "\n\n"
        patched_chunk += part
    out_parts.append(patched_chunk)

if patched_count != len(scores):
    raise SystemExit(f"patched count mismatch: patched={patched_count}, scores={len(scores)}")

merged = "".join(out_parts)
if not merged.endswith("\n"):
    merged += "\n"

regular_count = merged.count("LLM Judge（自动评审）")
thinking_count = merged.count("LLM Judge（thinking 自动评审）")
if regular_count != 110:
    raise SystemExit(f"regular judge block count mismatch: {regular_count}")
if thinking_count != 110:
    raise SystemExit(f"thinking judge block count mismatch: {thinking_count}")

REVIEW.write_text(merged, encoding="utf-8", newline="\n")
print(f"merged thinking judge blocks: {thinking_count}")
print(f"preserved regular judge blocks: {regular_count}")
print(REVIEW)