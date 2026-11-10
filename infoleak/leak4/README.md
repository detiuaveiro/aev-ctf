# leak4

**Category:** infoleak · **Difficulty:** medium · **Points:** 200
**Formerly:** leak-git — renamed so the name no longer hints at the leak class.

A medium web challenge: The .git directory is exposed and history holds the flag.

**Lab address:** http://leak4.chal.deti:8013

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8013
python solution/solve.py    # should print the flag
```

## Notes
- The home page carries a small in-app hint (link/form/image/button) that
  points students toward where to look without naming the vulnerability.
- The flag is read from the FLAG env var at runtime (per-student injection),
  except where noted otherwise.
- CI runs the reference solve on every push via `scripts/verify.py`.
