# dvwa

**Category:** web · **Difficulty:** intro→intermediate · **Points:** 100

DVWA — a PHP/MySQL app for practicing web security across four difficulty levels.
Find the per-student flag through one of the exercises.

**Lab address:** http://dvwa.chal.deti:8082

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8082
```
## Bring it up in the lab
```bash
./deploy.sh container up web/dvwa flag_file=/etc/lab/flags/dvwa
```
