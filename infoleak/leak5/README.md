# leak5

**Category:** infoleak · **Difficulty:** hard · **Points:** 250
**Formerly:** leak-idor-api — renamed so the name no longer hints at the leak class.

A hard web challenge: An API lets you enumerate users and a hidden field leaks the flag.

**Lab address:** http://leak5.chal.deti:8014

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8014
python solution/solve.py    # should print the flag
```

## Notes
- The home page carries a small in-app hint (link/form/image/button) that
  points students toward where to look without naming the vulnerability.
- The flag is read from the FLAG env var at runtime (per-student injection),
  except where noted otherwise.
- CI runs the reference solve on every push via `scripts/verify.py`.
