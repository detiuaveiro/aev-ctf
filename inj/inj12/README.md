# inj12

**Category:** inj · **Difficulty:** hard · **Points:** 250

A session-restore service. You hand it a saved workspace — a serialized
object — and it hands back a preview. Serialized is not the same as inert:
reconstruction is execution, and the preview is only as trustworthy as the
object that produced it.

**Lab address:** http://inj12.chal.deti:8051

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8051
python solution/solve.py    # should print the flag
```
