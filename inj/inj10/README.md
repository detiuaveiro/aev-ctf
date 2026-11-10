# inj10

**Category:** inj · **Difficulty:** hard · **Points:** 250

A diagnostics dashboard with a plugin system: upload a script, and the tool
runner searches the plugin path *before* the stock tools. The names are
validated. The contents are not.

**Lab address:** http://inj10.chal.deti:8049

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8049
python solution/solve.py    # should print the flag
```
