# juiceshop

**Category:** web · **Difficulty:** intro→intermediate · **Points:** 100

OWASP Juice Shop — a deliberately insecure e-commerce store. Find the per-student
flag through the app's own challenges.

**Lab address:** http://juiceshop.chal.deti:3000

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:3000
```
## Bring it up in the lab
```bash
./deploy.sh container up web/juiceshop flag_file=/etc/lab/flags/juiceshop
```
