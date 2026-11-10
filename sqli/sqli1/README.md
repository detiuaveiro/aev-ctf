# Staff Portal (sqli)

Category: sqli · Port: 8030 · DNS: sqli1.chal.deti

A little door for the IT crew.
One wrong line and it swings wide.
Who's on shift today?

On-shift sign-in for a fictional IT support crew. Sign in and the shift
board greets you with the day's IT announcement.

## Stack
Flask + **SQLite** (stdlib `sqlite3`; the DB file lives on the `/var/lib/app`
tmpfs and is seeded from the `FLAG` env every start).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8030
docker compose down -v
```
