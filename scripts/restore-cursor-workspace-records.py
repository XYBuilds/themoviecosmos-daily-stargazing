#!/usr/bin/env python3
"""
Restore Cursor Agent chat history for themoviecosmos-daily-stargazing.

Problem: Cursor created a new workspace storage ID for the same folder path.
  OLD (has 199 conversations): ba22009a388c8a62ccf0ad32e9d62a7e
  NEW (currently active):      21a128b166f72e212b3e64bdb21514fd

IMPORTANT: Close ALL Cursor windows before running this script.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OLD_WS = "ba22009a388c8a62ccf0ad32e9d62a7e"
NEW_WS = "21a128b166f72e212b3e64bdb21514fd"
TARGET_PATH = "themoviecosmos-daily-stargazing"

CURSOR_ROAMING = Path(r"C:\Users\pexy9\AppData\Roaming\Cursor\User")
GLOBAL_DB = CURSOR_ROAMING / "globalStorage" / "state.vscdb"
OLD_WS_DIR = CURSOR_ROAMING / "workspaceStorage" / OLD_WS
NEW_WS_DIR = CURSOR_ROAMING / "workspaceStorage" / NEW_WS
BACKUP_ROOT = CURSOR_ROAMING / "workspaceStorage"


def die(msg: str, code: int = 1) -> None:
    print(f"\n[ERROR] {msg}", file=sys.stderr)
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
            if image.lower() in result.stdout.lower():
                return True
        except Exception:
            pass
    return False


def replace_ws_id(raw) -> tuple[object, int]:
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="surrogateescape")
        if OLD_WS not in text:
            return raw, 0
        new_text = text.replace(OLD_WS, NEW_WS)
        return new_text.encode("utf-8", errors="surrogateescape"), text.count(OLD_WS)
    text = raw if isinstance(raw, str) else str(raw)
    if OLD_WS not in text:
        return raw, 0
    return text.replace(OLD_WS, NEW_WS), text.count(OLD_WS)


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


def backup_all(backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_db(GLOBAL_DB)
    checkpoint_db(OLD_WS_DIR / "state.vscdb")
    checkpoint_db(NEW_WS_DIR / "state.vscdb")

    shutil.copy2(GLOBAL_DB, backup_dir / "state.vscdb.global")
    if OLD_WS_DIR.exists():
        shutil.copytree(OLD_WS_DIR, backup_dir / f"workspace_{OLD_WS}", dirs_exist_ok=True)
    if NEW_WS_DIR.exists():
        shutil.copytree(NEW_WS_DIR, backup_dir / f"workspace_{NEW_WS}", dirs_exist_ok=True)
    print(f"Backup: {backup_dir}")


def copy_workspace_storage() -> None:
    if not OLD_WS_DIR.exists():
        die(f"Old workspace storage not found: {OLD_WS_DIR}")

    checkpoint_db(OLD_WS_DIR / "state.vscdb")
    checkpoint_db(NEW_WS_DIR / "state.vscdb")

    NEW_WS_DIR.mkdir(parents=True, exist_ok=True)

    for item in OLD_WS_DIR.iterdir():
        if item.name.endswith(("-wal", "-shm")):
            continue
        dest = NEW_WS_DIR / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # workspace.json must still point to the same folder
    workspace_json = NEW_WS_DIR / "workspace.json"
    workspace_json.write_text(
        '{\n  "folder": "file:///t%3A/themoviecosmos-daily-stargazing"\n}',
        encoding="utf-8",
    )
    checkpoint_db(NEW_WS_DIR / "state.vscdb")
    print("Copied old workspace storage -> new workspace storage")


def migrate_global_db() -> None:
    checkpoint_db(GLOBAL_DB)
    conn = sqlite3.connect(GLOBAL_DB)
    cur = conn.cursor()

    # composer headers
    cur.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'")
    row = cur.fetchone()
    if not row:
        die("composer.composerHeaders not found in global DB")
    headers = json.loads(row[0])
    migrated = 0
    for composer in headers.get("allComposers", []):
        wi = composer.get("workspaceIdentifier")
        if not isinstance(wi, dict):
            continue
        fs = (wi.get("uri") or {}).get("fsPath", "")
        if wi.get("id") == OLD_WS and TARGET_PATH in fs.replace("\\", "/").lower():
            wi["id"] = NEW_WS
            migrated += 1
    cur.execute(
        "UPDATE ItemTable SET value = ? WHERE key = 'composer.composerHeaders'",
        (json.dumps(headers),),
    )
    print(f"Migrated composer headers: {migrated}")

    # ItemTable string values
    cur.execute("SELECT key, value FROM ItemTable WHERE value LIKE ?", (f"%{OLD_WS}%",))
    item_updates = 0
    for key, value in cur.fetchall():
        if key == "composer.composerHeaders":
            continue
        new_value, count = replace_ws_id(value)
        if count:
            cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (new_value, key))
            item_updates += 1
            print(f"  ItemTable: {key} ({count})")
    print(f"ItemTable updates: {item_updates}")

    # cursorDiskKV key renames
    cur.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE ?", (f"inlineDiff:{OLD_WS}:%",))
    inline_rows = cur.fetchall()
    for key, value in inline_rows:
        new_key, _ = replace_ws_id(key)
        cur.execute("DELETE FROM cursorDiskKV WHERE key = ?", (key,))
        cur.execute("INSERT OR REPLACE INTO cursorDiskKV (key, value) VALUES (?, ?)", (new_key, value))
    print(f"inlineDiff key migrations: {len(inline_rows)}")

    # cursorDiskKV values
    cur.execute("SELECT key, value FROM cursorDiskKV WHERE value LIKE ?", (f"%{OLD_WS}%",))
    kv_updates = 0
    for key, value in cur.fetchall():
        new_value, count = replace_ws_id(value)
        if count:
            cur.execute("UPDATE cursorDiskKV SET value = ? WHERE key = ?", (new_value, key))
            kv_updates += 1
    print(f"cursorDiskKV value updates: {kv_updates}")

    conn.commit()
    conn.close()
    checkpoint_db(GLOBAL_DB)


def verify() -> bool:
    conn = sqlite3.connect(GLOBAL_DB)
    cur = conn.cursor()
    cur.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'")
    headers = json.loads(cur.fetchone()[0])
    old_count = new_count = 0
    for composer in headers.get("allComposers", []):
        if composer.get("type") != "head":
            continue
        wi = composer.get("workspaceIdentifier") or {}
        fs = (wi.get("uri") or {}).get("fsPath", "")
        if TARGET_PATH not in fs.replace("\\", "/").lower():
            continue
        if wi.get("id") == OLD_WS:
            old_count += 1
        elif wi.get("id") == NEW_WS:
            new_count += 1
    cur.execute("SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE ?", (f"inlineDiff:{OLD_WS}:%",))
    inline_old = cur.fetchone()[0]
    conn.close()

    print("\n=== Verification ===")
    print(f"Stargazing composers on OLD id: {old_count}")
    print(f"Stargazing composers on NEW id: {new_count}")
    print(f"Remaining inlineDiff OLD keys: {inline_old}")
    ok = old_count == 0 and new_count > 0 and inline_old == 0
    print("Result:", "OK" if ok else "FAILED")
    return ok


def main() -> None:
    print("=" * 60)
    print("Cursor workspace record restore")
    print("=" * 60)

    if cursor_is_running():
        die(
            "Cursor is still running.\n"
            "Please close ALL Cursor windows, then run this script again."
        )

    if not GLOBAL_DB.exists():
        die(f"Global DB not found: {GLOBAL_DB}")

    backup_dir = BACKUP_ROOT / f"_backup_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_all(backup_dir)
    copy_workspace_storage()
    migrate_global_db()

    if not verify():
        die(
            "Verification failed. Your backup is at:\n"
            f"  {backup_dir}\n"
            "Do not reopen Cursor until this is resolved."
        )

    print("\nDone.")
    print("Now reopen Cursor and open: t:\\themoviecosmos-daily-stargazing")
    print(f"Backup kept at: {backup_dir}")


if __name__ == "__main__":
    main()
