#!/usr/bin/env python3
r"""
Restore Cursor Agent chat headers for the exact
`t-themoviecosmos-daily-stargazing` project.

This script intentionally does NOT search by project keywords across Cursor's
history. It only uses the parent transcript UUIDs under:

  C:\Users\pexy9\.cursor\projects\t-themoviecosmos-daily-stargazing\agent-transcripts

For matching composer headers, it rewrites the workspace id to the current
workspaceStorage id for:

  T:\themoviecosmos-daily-stargazing

IMPORTANT: Close ALL Cursor windows before running this script.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

TARGET_PROJECT = "t-themoviecosmos-daily-stargazing"
TARGET_FOLDER_URI = "file:///t%3A/themoviecosmos-daily-stargazing"
TARGET_WORKSPACE_ID = "21a128b166f72e212b3e64bdb21514fd"
KNOWN_WRONG_WORKSPACE_ID = "11d886b61fa79e15674b233a80bd6098"
LEGACY_OLD_WORKSPACE_ID = "ba22009a388c8a62ccf0ad32e9d62a7e"

CURSOR_PROJECT_DIR = Path(r"C:\Users\pexy9\.cursor\projects") / TARGET_PROJECT
TRANSCRIPTS_DIR = CURSOR_PROJECT_DIR / "agent-transcripts"
CURSOR_USER_DIR = Path(r"C:\Users\pexy9\AppData\Roaming\Cursor\User")
GLOBAL_DB = CURSOR_USER_DIR / "globalStorage" / "state.vscdb"
WORKSPACE_STORAGE_DIR = CURSOR_USER_DIR / "workspaceStorage"
TARGET_WORKSPACE_DIR = WORKSPACE_STORAGE_DIR / TARGET_WORKSPACE_ID
TARGET_WORKSPACE_DB = TARGET_WORKSPACE_DIR / "state.vscdb"

COMPOSER_HEADERS_KEY = "composer.composerHeaders"
BACKUP_PREFIX = "_backup_stargazing_exact_restore"


def die(message: str, code: int = 1) -> None:
    print(f"\n[ERROR] {message}", file=sys.stderr)
    sys.exit(code)


def cursor_is_running() -> bool:
    for image in ("Cursor.exe", "cursor.exe"):
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {image}", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            continue
        if image.lower() in result.stdout.lower():
            return True
    return False


def checkpoint_db(db_path: Path) -> None:
    if not db_path.exists():
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.commit()
    finally:
        conn.close()

    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db_path) + suffix)
        if sidecar.exists():
            sidecar.unlink()


def backup_path(path: Path, backup_dir: Path, name: str) -> None:
    if not path.exists():
        return
    dest = backup_dir / name
    if path.is_dir():
        shutil.copytree(path, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(path, dest)


def backup_cursor_state() -> Path:
    backup_dir = WORKSPACE_STORAGE_DIR / f"{BACKUP_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_db(GLOBAL_DB)
    checkpoint_db(TARGET_WORKSPACE_DB)
    wrong_db = WORKSPACE_STORAGE_DIR / KNOWN_WRONG_WORKSPACE_ID / "state.vscdb"
    checkpoint_db(wrong_db)
    legacy_db = WORKSPACE_STORAGE_DIR / LEGACY_OLD_WORKSPACE_ID / "state.vscdb"
    checkpoint_db(legacy_db)

    backup_path(GLOBAL_DB, backup_dir, "global-state.vscdb")
    backup_path(TARGET_WORKSPACE_DIR, backup_dir, f"workspace-{TARGET_WORKSPACE_ID}")
    backup_path(WORKSPACE_STORAGE_DIR / KNOWN_WRONG_WORKSPACE_ID, backup_dir, f"workspace-{KNOWN_WRONG_WORKSPACE_ID}")
    backup_path(WORKSPACE_STORAGE_DIR / LEGACY_OLD_WORKSPACE_ID, backup_dir, f"workspace-{LEGACY_OLD_WORKSPACE_ID}")

    return backup_dir


def load_transcript_ids() -> set[str]:
    if not TRANSCRIPTS_DIR.exists():
        die(f"Transcript directory not found: {TRANSCRIPTS_DIR}")

    ids = {path.name for path in TRANSCRIPTS_DIR.iterdir() if path.is_dir()}
    if not ids:
        die(f"No transcript parent directories found: {TRANSCRIPTS_DIR}")
    return ids


def load_headers(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute(
        "SELECT value FROM ItemTable WHERE key = ?",
        (COMPOSER_HEADERS_KEY,),
    ).fetchone()
    if row is None:
        die(f"{COMPOSER_HEADERS_KEY!r} not found in global DB")
    return json.loads(row[0])


def composer_id(header: dict[str, Any]) -> str | None:
    value = header.get("composerId") or header.get("id")
    return value if isinstance(value, str) else None


def workspace_id(header: dict[str, Any]) -> str:
    workspace = header.get("workspaceIdentifier")
    if not isinstance(workspace, dict):
        return "<missing>"
    value = workspace.get("id")
    return value if isinstance(value, str) and value else "<missing>"


def ensure_workspace_identifier(header: dict[str, Any]) -> dict[str, Any]:
    workspace = header.get("workspaceIdentifier")
    if not isinstance(workspace, dict):
        workspace = {}
        header["workspaceIdentifier"] = workspace

    workspace["id"] = TARGET_WORKSPACE_ID
    uri = workspace.get("uri")
    if not isinstance(uri, dict):
        uri = {}
        workspace["uri"] = uri
    uri["$mid"] = uri.get("$mid") or 1
    uri["fsPath"] = "t:\\themoviecosmos-daily-stargazing"
    uri["external"] = TARGET_FOLDER_URI
    uri["path"] = "/t:/themoviecosmos-daily-stargazing"
    uri["scheme"] = "file"
    return workspace


def summarize(headers: list[dict[str, Any]], transcript_ids: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for header in headers:
        cid = composer_id(header)
        if cid in transcript_ids:
            counts[workspace_id(header)] += 1
    return counts


def write_target_workspace_json() -> None:
    TARGET_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_WORKSPACE_DIR / "workspace.json").write_text(
        '{\n  "folder": "file:///t%3A/themoviecosmos-daily-stargazing"\n}',
        encoding="utf-8",
    )


def restore_headers() -> tuple[dict[str, Any], dict[str, Any]]:
    transcript_ids = load_transcript_ids()
    conn = sqlite3.connect(GLOBAL_DB)
    try:
        headers_json = load_headers(conn)
        all_headers = headers_json.get("allComposers")
        if not isinstance(all_headers, list):
            die("composer.composerHeaders has no allComposers list")

        before = summarize(all_headers, transcript_ids)
        matched_ids: set[str] = set()
        changed = 0
        already_target = 0
        skipped_non_project = 0

        for header in all_headers:
            if not isinstance(header, dict):
                continue
            cid = composer_id(header)
            if cid not in transcript_ids:
                skipped_non_project += 1
                continue

            matched_ids.add(cid)
            if workspace_id(header) == TARGET_WORKSPACE_ID:
                already_target += 1
                ensure_workspace_identifier(header)
                continue

            ensure_workspace_identifier(header)
            changed += 1

        conn.execute(
            "UPDATE ItemTable SET value = ? WHERE key = ?",
            (json.dumps(headers_json, ensure_ascii=False, separators=(",", ":")), COMPOSER_HEADERS_KEY),
        )
        conn.commit()

        after = summarize(all_headers, transcript_ids)
        missing_ids = sorted(transcript_ids - matched_ids)

        return headers_json, {
            "transcript_parent_ids": len(transcript_ids),
            "matched_headers": len(matched_ids),
            "changed_headers": changed,
            "already_target": already_target,
            "missing_headers": len(missing_ids),
            "missing_header_ids_sample": missing_ids[:10],
            "skipped_non_project_headers": skipped_non_project,
            "workspace_counts_before": dict(before),
            "workspace_counts_after": dict(after),
        }
    finally:
        conn.close()
        checkpoint_db(GLOBAL_DB)


def verify() -> dict[str, Any]:
    transcript_ids = load_transcript_ids()
    conn = sqlite3.connect(GLOBAL_DB)
    try:
        headers_json = load_headers(conn)
        all_headers = headers_json.get("allComposers", [])
        counts = summarize(all_headers, transcript_ids)
        matched = sum(counts.values())
        wrong = matched - counts.get(TARGET_WORKSPACE_ID, 0)
        return {
            "transcript_parent_ids": len(transcript_ids),
            "matched_headers": matched,
            "target_workspace_headers": counts.get(TARGET_WORKSPACE_ID, 0),
            "non_target_workspace_headers": wrong,
            "workspace_counts": dict(counts),
            "ok": matched > 0 and wrong == 0,
        }
    finally:
        conn.close()


def main() -> None:
    print("=" * 72)
    print("Cursor exact project Agent chat restore")
    print("=" * 72)
    print(f"Project: {TARGET_PROJECT}")
    print(f"Transcript source: {TRANSCRIPTS_DIR}")
    print(f"Target workspace id: {TARGET_WORKSPACE_ID}")
    print()

    if cursor_is_running():
        die("Cursor is still running. Close ALL Cursor windows, then run this script again.")
    if not GLOBAL_DB.exists():
        die(f"Global DB not found: {GLOBAL_DB}")
    if not TARGET_WORKSPACE_DIR.exists():
        die(f"Target workspace storage not found: {TARGET_WORKSPACE_DIR}")

    backup_dir = backup_cursor_state()
    print(f"Backup: {backup_dir}")

    write_target_workspace_json()
    _, stats = restore_headers()
    result = verify()

    print("\n=== Restore stats ===")
    print(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True))
    print("\n=== Verification ===")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    if not result["ok"]:
        die(
            "Verification failed. Cursor has not been reopened. Backup is at:\n"
            f"  {backup_dir}\n"
            "Keep Cursor closed and inspect the stats above."
        )

    print("\nDone.")
    print("Reopen Cursor and open: T:\\themoviecosmos-daily-stargazing")
    print(f"Backup kept at: {backup_dir}")


if __name__ == "__main__":
    main()