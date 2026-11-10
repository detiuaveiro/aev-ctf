# inj14

**Category:** inj · **Difficulty:** hard · **Points:** 200

An admin diagnostics API behind a WAF. The gate inspects every command
before the app sees it — and the app, to be safe, inspects it a second
time. Two readers of the same request rarely agree on what it says.

**Lab address:** http://inj14.chal.deti:8053

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8053
python solution/solve.py    # should print the flag
```
