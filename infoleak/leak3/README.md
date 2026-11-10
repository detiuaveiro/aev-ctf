# leak3

**Category:** infoleak · **Difficulty:** easy · **Points:** 100
**Formerly:** leak-dir-listing — renamed so the name no longer hints at the leak class.

A easy web challenge: Directory listing is enabled and a flag file is in plain sight.

**Lab address:** http://leak3.chal.deti:8012

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8012
python solution/solve.py    # should print the flag
```

## Notes
- The home page carries a small in-app hint (link/form/image/button) that
  points students toward where to look without naming the vulnerability.
- The flag is read from the FLAG env var at runtime (per-student injection),
  except where noted otherwise.
- CI runs the reference solve on every push via `scripts/verify.py`.
