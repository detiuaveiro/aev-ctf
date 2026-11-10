# leak7

**Category:** infoleak · **Difficulty:** hard · **Points:** 300
**Formerly:** leak-oracle — renamed so the name no longer hints at the leak class.

A hard web challenge: A prefix oracle lets you reconstruct the flag character by character.

**Lab address:** http://leak7.chal.deti:8016

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8016
python solution/solve.py    # should print the flag
```

## Notes
- The home page carries a small in-app hint (link/form/image/button) that
  points students toward where to look without naming the vulnerability.
- The flag is read from the FLAG env var at runtime (per-student injection),
  except where noted otherwise.
- CI runs the reference solve on every push via `scripts/verify.py`.
