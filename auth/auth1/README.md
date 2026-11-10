# auth1

**Category:** auth · **Difficulty:** easy · **Points:** 100

NetGuard Router's admin console. The landing page is public; the admin
console asks for a username and password through your browser's own login
prompt.

**Lab address:** http://auth1.chal.deti:8060

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8060
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
