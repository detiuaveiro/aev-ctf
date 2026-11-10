# auth12

**Category:** auth · **Difficulty:** easy · **Points:** 100

Cornerstone CMS, the marketing site's content manager.

**Lab address:** http://auth12.chal.deti:8071

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8071
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
