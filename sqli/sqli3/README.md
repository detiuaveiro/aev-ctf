# PhotoVault (sqli)

Category: sqli · Port: 8032 · DNS: sqli3.chal.deti

Every frame has a number.
Numbers line up in the dark.
Count the columns.

A small photo gallery of the places we've been. Open a photo to read
its caption.

## Stack
Flask + **SQLite** (stdlib `sqlite3`; the DB file lives on the `/var/lib/app`
tmpfs and is seeded from the `FLAG` env every start).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8032
docker compose down -v
```
