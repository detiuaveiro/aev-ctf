# sqli8 (sqli) — TransferOps Console

Category: sqli · Port: 8037 · DNS: sqli8.chal.deti · Value: 500

> The export is yours.
> It writes whatever you name.
> Some rows are kept out.

TransferOps Console is internal tooling for a data-transfer fleet: it
renders the `transfers`, `routes` and `queues` tables, and lets anyone on
the network *export a report* for a table — the writer takes the table
name from the request, writes the result to the shared public reports
folder (`/data/public/reports`, a tmpfs), and the same app serves that
folder back at `/reports/<file>`. The console never renders everything
that lives in its database.

## Stack
Flask + **MariaDB** (embedded; the datadir is a build-time-provisioned
image volume, re-seeded from the `FLAG` env every start). MariaDB is used
because the technique needs MySQL-specific mechanics (`INTO OUTFILE`, and
the `FILE` privilege on the `app` DB user).

## Local verification
```
docker compose up -d --build
python solution/solve.py http://127.0.0.1:8037
docker compose down -v
```
