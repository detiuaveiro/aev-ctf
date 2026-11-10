# sqli7 (sqli) — Linkly

Category: sqli · Port: 8036 · DNS: sqli7.chal.deti · Value: 500

> We fetch the link for you.
> Whatever it says, we'll ask it.
> Send it somewhere you can see.

Linkly is a link-preview service: paste a URL and Linkly fetches it, then
shows you what it got. The preview page (`/l/<n>`) builds its query by
concatenating the id straight from the URL — and the app fetches *every*
link it renders, whatever row the query happens to return.

## Stack
Flask + **SQLite** (stdlib `sqlite3`; the DB file lives on the `/var/lib/app`
tmpfs and is seeded from the `FLAG` env every start). No DB daemon, no
MySQL-specific mechanics — the trick here is that the app performs an HTTP
request on your behalf.

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8036
docker compose down -v
```
