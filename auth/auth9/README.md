# auth9

**Category:** auth · **Difficulty:** medium · **Points:** 150

DeskHero Helpdesk, the IT ticketing system. Agents sign in to work tickets;
there's an on-call rotation refresh running in the background.

**Lab address:** http://auth9.chal.deti:8068

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8068
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
