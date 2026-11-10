# mutillidae

**Category:** web · **Difficulty:** intro→intermediate · **Points:** 100

Mutillidae — a deliberately vulnerable web app for security training across the
OWASP Top 10. Find the per-student flag through one of the labs.

**Lab address:** http://mutillidae.chal.deti:8083

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8083
```
## Bring it up in the lab
```bash
./deploy.sh container up web/mutillidae flag_file=/etc/lab/flags/mutillidae
```
