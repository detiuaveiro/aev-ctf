# auth13

**Category:** auth · **Difficulty:** medium · **Points:** 150

RemoteLink VPN. Seeded account: `vpnuser` (password not given — nothing
stops you from trying a few).

**Lab address:** http://auth13.chal.deti:8072

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8072
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
