# inj1

**Category:** inj · **Difficulty:** easy · **Points:** 100

A library network dashboard whose node health check answers from a shell.
The dashboard has no secret of its own — but the person who can make the
shell run a second command can read anything the service user can read.

**Lab address:** http://inj1.chal.deti:8040

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8040
python solution/solve.py    # should print the flag
```
