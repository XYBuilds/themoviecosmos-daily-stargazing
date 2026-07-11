#!/usr/bin/env python3
"""Safe status check for the exact stargazing Cursor project."""
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

TARGET_PROJECT = "t-themoviecosmos-daily-stargazing"
TARGET_WORKSPACE_ID = "21a128b166f72e212b3e64bdb21514fd"
TRANSCRIPTS_DIR = Path(r"C:\Users\pexy9\.cursor\projects") / TARGET_PROJECT / "agent-transcripts"
GLOBAL_DB = Path(r"C:\Users\pexy9\AppData\Roaming\Cursor\User\globalStorage\state.vscdb")
COMPOSER_HEADERS_KEY = "composer.composerHeaders"


def composer_id(header: dict[str, Any]) -> str | None:
    value = header.get("composerId") or header.get("id")
    return value if isinstance(value, str) else None


def workspace_id(header: dict[str, Any]) -> str:
    workspace = header.get("workspaceIdentifier")
    if not isinstance(workspace, dict):
        return "<missing>"
    value = workspace.get("id")
    return value if isinstance(value, str) and value else "<missing>"


def main() -> None:
    transcript_ids = {path.name for path in TRANSCRIPTS_DIR.iterdir() if path.is_dir()}

    conn = sqlite3.connect(GLOBAL_DB)
    try:
        row = conn.execute(
            "SELECT value FROM ItemTable WHERE key = ?",
            (COMPOSER_HEADERS_KEY,),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"{COMPOSER_HEADERS_KEY!r} not found")
        headers = json.loads(row[0]).get("allComposers", [])
    finally:
        conn.close()

    counts: Counter[str] = Counter()
    matched_ids: set[str] = set()
    for header in headers:
        if not isinstance(header, dict):
            continue
        cid = composer_id(header)
        if cid in transcript_ids:
            matched_ids.add(cid)
            counts[workspace_id(header)] += 1

    target = counts.get(TARGET_WORKSPACE_ID, 0)
    non_target = sum(counts.values()) - target

    print(f"Project: {TARGET_PROJECT}")
    print(f"Transcript parent ids: {len(transcript_ids)}")
    print(f"Headers matched by transcript id: {len(matched_ids)}")
    print("Workspace counts:")
    for wid, count in counts.most_common():
        marker = " <= target" if wid == TARGET_WORKSPACE_ID else ""
        print(f"  {wid}: {count}{marker}")
    print(f"Missing headers: {len(transcript_ids - matched_ids)}")

    if target > 0 and non_target == 0:
        print("Status: OK (all matched project chats point to the current workspace id)")
    elif non_target > 0:
        print("Status: NEEDS RESTORE (some matched project chats point to another workspace id)")
        print("Action: close ALL Cursor windows, then run restore-cursor-workspace-records.bat")
    else:
        print("Status: UNKNOWN (no matching project chat headers found)")


if __name__ == "__main__":
    main()