# The Daily Byte (sqli)

Category: sqli · Port: 8034 · DNS: sqli5.chal.deti

Pick a tag, read the titles.
Some lines appear, some don't.
Make one line the truth.

A small blog from the people who keep the lab running. Posts are grouped
under a handful of tags.

## Stack
Flask + **SQLite** (stdlib `sqlite3`; the DB file lives on the `/var/lib/app`
tmpfs and is seeded from the `FLAG` env every start).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8034
docker compose down -v
```
