# auth4

**Category:** auth · **Difficulty:** easy · **Points:** 100

ExpenseFlow, the company's expense-approval tool. Sign in with the employee
account below and submit a report — or see what a manager sees.

Seeded account: `employee` / `employee123`

**Lab address:** http://auth4.chal.deti:8063

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8063
python solution/solve.py    # should print the flag
```

## Notes
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
