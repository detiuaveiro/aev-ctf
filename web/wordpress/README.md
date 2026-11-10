# wordpress

**Category:** web · **Difficulty:** advanced · **Points:** 100

A stock WordPress site, freshly seeded. The core is older than it should be —
find out what ships with the platform and how far that gets you. The flag
lives outside the web root.

**Lab address:** http://wordpress.chal.deti:8084

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8084
```
## Bring it up in the lab
```bash
./deploy.sh container up web/wordpress flag_file=/etc/lab/flags/wordpress
```
