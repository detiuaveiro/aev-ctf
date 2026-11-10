# notes1

**Category:** web · **Difficulty:** intro · **Points:** 100
**Formerly:** idor-notes — renamed so the name no longer hints at the leak class.

A minimal notes app. You have a guest account (`guest / guest123`). Some notes
are more private than others — read the one you shouldn't be able to.

**Lab address:** http://notes1.chal.deti:8020

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8020
python solution/solve.py    # should print the flag
```
