# leak10

**Category:** infoleak · **Difficulty:** introductory · **Points:** 75
**Formerly:** leak-verbose-error — renamed so the name no longer hints at the leak class.

A introductory web challenge: The flag is exposed in a verbose stack trace.

**Lab address:** http://leak10.chal.deti:8019

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8019
python solution/solve.py    # should print the flag
```

## Notes
- The home page carries a small in-app hint (link/form/image/button) that
  points students toward where to look without naming the vulnerability.
- The flag is read from the FLAG env var at runtime (per-student injection),
  except where noted otherwise.
- CI runs the reference solve on every push via `scripts/verify.py`.
