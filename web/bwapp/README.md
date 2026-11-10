# bwapp

**Category:** web · **Difficulty:** intro→intermediate · **Points:** 100

bWAPP — a deliberately vulnerable PHP web application with 100+ exercises across
the OWASP Top 10. Find the per-student flag through one of the exercises.

**Lab address:** http://bwapp.chal.deti:8081

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8081
```
## Bring it up in the lab
```bash
./deploy.sh container up web/bwapp flag_file=/etc/lab/flags/bwapp
```
