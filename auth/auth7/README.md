# auth7

**Category:** auth · **Difficulty:** medium · **Points:** 150

ConnectAPI Partner Gateway. Partners sign in to get an API token. Seeded
partner: `acme` / `acmepass`.

**Lab address:** http://auth7.chal.deti:8066

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8066
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
