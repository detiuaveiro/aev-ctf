# Guestbook (sqli)

Category: sqli · Port: 8035 · DNS: sqli6.chal.deti

Every note gets the same thanks.
Sometimes it takes longer.
Measure the silence.

The shift guestbook. Sign it with a note for the next crew.

## Stack
Flask + **MariaDB** (embedded, single fixed user, seeded from the `FLAG`
env every start).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8035
docker compose down -v
```
