# Solution — sqli8 (TransferOps Console)

Out-of-band write. The "Export a report" form builds

    SELECT * FROM <table> WHERE <filter> INTO OUTFILE
    '/data/public/reports/<table>.csv'

by concatenation, and the same app serves that folder at
`/reports/<file>`. The console renders only `transfers`, `routes` and
`queues` — but the writer takes the table name from the request and will
export *any* table in `appdb`.

1. Export the table the console never shows (the hint says rows are "kept
   out"; try obvious names — `vault`):

   `GET /report/vault`   → the app writes `/data/public/reports/vault.csv`
   via `INTO OUTFILE` (the `app` DB user carries the `FILE` privilege).
2. Download it: `GET /reports/vault.csv`. The flag sits in the `secret`
   column of the CSV.

`solve.py` does both steps and prints the flag.
