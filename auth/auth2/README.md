# auth2

**Category:** auth · **Difficulty:** easy · **Points:** 100

Harbor Wiki, the team's internal knowledge base. Most pages are public; a
few are meant for staff only.

**Lab address:** http://auth2.chal.deti:8061

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8061
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
