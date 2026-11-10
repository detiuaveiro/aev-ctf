# auth6

**Category:** auth · **Difficulty:** medium · **Points:** 150

Brightleaf runs a marketing microsite and its real ops app on the same
parent domain. For this lab, send `Host: marketing.auth6.chal.deti` to
reach the microsite, and the normal lab address for the app itself — both
answer on the one published port.

**Lab address:** http://auth6.chal.deti:8065

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8065
python solution/solve.py    # should print the flag
```

## Notes
- Lab simplification: a real deployment would use two actual DNS names
  sharing a `Domain=` cookie scope; this single container simulates both
  vhosts by branching on the `Host` header, so no second DNS record is
  needed. The vulnerability (overbroad cookie scope + session fixation) is
  unchanged.
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
