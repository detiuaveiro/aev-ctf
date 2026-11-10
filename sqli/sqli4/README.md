# DropLite (sqli)

Category: sqli · Port: 8033 · DNS: sqli4.chal.deti

You see names and sizes,
never the insides.
Ask, then count the answers.

A tiny file transfer service. Transfers show up as names and sizes;
links are only ever re-sent to the original uploader. You can search
the transfer index.

## Stack
Flask + **SQLite** (stdlib `sqlite3`; the DB file lives on the `/var/lib/app`
tmpfs and is seeded from the `FLAG` env every start).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8033
docker compose down -v
```
