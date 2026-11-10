# snmp1 — SNMP information leak

**Category:** network · **Difficulty:** introductory · **Points:** 100

The lab host runs an SNMP agent on UDP 161 with the default `public`
community. It answers anyone who asks — and it talks about itself.

**Lab address:** snmp1.chal.deti:8024/udp (community: `public`)

## Run it locally (staff)
```bash
docker compose up --build   # agent on UDP 161, published at 8024
python solution/solve.py    # should print the flag
```

## Notes
- The agent exposes standard MIB-II host info (the system group and a small
  interface table) **and** a private enterprise tree `1.3.6.1.4.1.99999.1.1.*`.
- The first private node is the *output of a status script* the agent runs on
  demand — that is where the flag lives.
- The flag is read from the `FLAG` env var at runtime (per-student injection).
- CI runs the reference solve on every push via `scripts/verify.py`.
