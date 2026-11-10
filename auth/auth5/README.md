# auth5

**Category:** auth · **Difficulty:** medium · **Points:** 150

Alma Portal, the university's course catalog and advisor dashboard. Guests
browse freely; staff sign in for advisor tools. There's a registrar "link
checker" bot mentioned on the landing page.

**Lab address:** http://auth5.chal.deti:8064

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8064
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
