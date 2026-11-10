# auth8

**Category:** auth · **Difficulty:** medium · **Points:** 150

PocketBank Lite. Seeded account: `customer` / `customer123`.

**Lab address:** http://auth8.chal.deti:8067

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8067
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
