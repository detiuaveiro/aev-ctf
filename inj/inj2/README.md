# inj2

**Category:** inj · **Difficulty:** easy · **Points:** 100

A store label service that "sanitizes" its input before handing it to a
shell. The sanitizer is a short blacklist — short enough that one character
the developer never thought about still splits the command.

**Lab address:** http://inj2.chal.deti:8041

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8041
python solution/solve.py    # should print the flag
```
