# auth14

**Category:** auth · **Difficulty:** easy · **Points:** 100

FernBank Online. There's a public ops diagnostics page, and a nightly
monitoring probe that signs in as the branch manager.

**Lab address:** http://auth14.chal.deti:8073

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8073
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
