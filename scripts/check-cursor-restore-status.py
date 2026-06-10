#!/usr/bin/env python3
"""Quick status check - safe to run while Cursor is open."""
import json
import sqlite3

OLD = "ba22009a388c8a62ccf0ad32e9d62a7e"
NEW = "21a128b166f72e212b3e64bdb21514fd"
TARGET = "themoviecosmos-daily-stargazing"
gdb = r"C:\Users\pexy9\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"

conn = sqlite3.connect(gdb)
cur = conn.cursor()
cur.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'")
headers = json.loads(cur.fetchone()[0])
old = new = 0
for c in headers.get("allComposers", []):
    if c.get("type") != "head":
        continue
    wi = c.get("workspaceIdentifier") or {}
    fs = (wi.get("uri") or {}).get("fsPath", "")
    if TARGET not in fs.replace("\\", "/").lower():
        continue
    if wi.get("id") == OLD:
        old += 1
    elif wi.get("id") == NEW:
        new += 1
print(f"Stargazing conversations -> OLD id: {old}, NEW id: {new}")
if old > 0 and new < old:
    print("Status: NEEDS RESTORE (close Cursor, then run restore-cursor-workspace-records.bat)")
elif old == 0 and new > 0:
    print("Status: OK (records point to current workspace id)")
else:
    print("Status: UNKNOWN")
conn.close()
