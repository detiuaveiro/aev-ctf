# auth11

**Category:** auth · **Difficulty:** medium · **Points:** 150

InboxNow Webmail. Seeded account: `user` / `user123`.

**Lab address:** http://auth11.chal.deti:8070

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8070
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
