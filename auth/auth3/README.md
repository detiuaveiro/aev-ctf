# auth3

**Category:** auth · **Difficulty:** easy · **Points:** 100

QuickShip Tracker. Your shipment confirmation includes a personal tracking
link — no account needed.

**Lab address:** http://auth3.chal.deti:8062

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8062
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
