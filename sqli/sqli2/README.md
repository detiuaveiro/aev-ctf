# TechBazaar Search (sqli)

Category: sqli · Port: 8031 · DNS: sqli2.chal.deti

Find it by name, or a part.
The shelves talk when ruffled.
What's in the back room?

The little parts counter on Canal Street. Ask for anything by name;
the search tells you what is on the shelves.

## Stack
Flask + **MariaDB** (embedded, single fixed user, seeded from the `FLAG`
env every start). The search shows the database's own words when it
gets ruffled.

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8031
docker compose down -v
```
