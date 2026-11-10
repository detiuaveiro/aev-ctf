# inj11

**Category:** inj · **Difficulty:** hard · **Points:** 200

A log-shipper control panel. You save a setting; a different piece of the
service acts on it later. The setting is validated when it is stored — for
being a path. What happens to it when it is executed is nobody's job.

**Lab address:** http://inj11.chal.deti:8050

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8050
python solution/solve.py    # should print the flag
```
