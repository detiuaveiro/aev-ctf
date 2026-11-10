# auth10

**Category:** auth · **Difficulty:** easy · **Points:** 100

PeopleFirst HR, the company's employee self-service portal. The front page
lists the team; sign in to see your own record.

**Lab address:** http://auth10.chal.deti:8069

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8069
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
