#!/bin/bash
# SQLi template entrypoint: embedded MariaDB + Flask app in one container.
#
# Runs as a SINGLE fixed user (ctf). The lab runs with DropCapability=ALL +
# read-only rootfs, which strips CAP_SETUID / CAP_CHOWN / CAP_DAC_OVERRIDE —
# so there is deliberately no privilege drop and no chown here. The DB is
# provisioned at build time (the datadir VOLUME carries the system tables +
# the 'app' DB user + an empty appdb); this entrypoint only starts the server
# and loads the seeded data.
#
# The flag arrives as the live /flag/flag file (lab rolling model; the FLAG
# env — podman secret or local compose — is the fallback when the mount is
# absent) and is interpolated into seed.sql. The flag never lives in the image.
set -euo pipefail

# Flag source (lab rolling model, reseed variant — see the challenge.yml
# `reseed` key): the LIVE flag file /flag/flag (a per-challenge directory
# bind-mounted ro from the host flag folder) wins over the FLAG env (podman
# secret / local compose fallback). Rotation rewrites the file; this
# entrypoint runs on every (re)start, so a restarted container re-seeds the
# database from the CURRENT flag — all seed data + the new flag at the
# __FLAG__ placeholder.
FLAG_SOURCE="FLAG env (podman secret / compose)"
if [[ -r /flag/flag ]]; then
  v="$(< /flag/flag)"
  if [[ -n "$v" ]]; then
    export FLAG="$v"
    FLAG_SOURCE="live /flag/flag file"
  fi
fi
# GOTCHA: never write FLAG="${FLAG:-flag{...}}" — the first '}' in the default
# closes the ${...} expansion and a literal '}' is appended to the env value.
[[ -n "${FLAG:-}" ]] || export FLAG='flag{local_verify}'

# /data/public/reports is a writable tmpfs mount (see challenge.container /
# docker-compose.yml) — the INTO OUTFILE target for the OOB-write challenge.
mkdir -p /data/public/reports

# Start mariadbd as ourselves (ctf). The datadir is the VOLUME /var/lib/mysql,
# owned by ctf at build time, so no --user / setuid is needed. The unix socket
# and pid file live in the datadir (ctf-owned) — /run is NOT writable by ctf
# under the lab's read-only + capability-drop flags, so we deliberately
# avoid it. A stale pid file (crash-restart without a volume wipe) is cleared.
rm -f /var/lib/mysql/mysqld.pid
mariadbd --datadir=/var/lib/mysql \
         --socket=/var/lib/mysql/mysqld.sock \
         --pid-file=/var/lib/mysql/mysqld.pid \
         --bind-address=127.0.0.1 --skip-log-bin &
MYSQD_PID=$!

# All DB access is loopback TCP as the 'app' DB user (created at build time).
db() { mysql -h 127.0.0.1 -u app -papppass "$@"; }

# Wait for readiness (30s).
for _ in $(seq 1 30); do
  if db -e "SELECT 1" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$MYSQD_PID" 2>/dev/null; then
    echo "mariadbd died during start" >&2
    exit 1
  fi
  sleep 1
done
db -e "SELECT 1" >/dev/null   # hard-fail if the server never came up

# Load the seed (flag interpolated). Idempotent by contract: seed.sql uses
# CREATE TABLE IF NOT EXISTS + upsert, so a re-run within a container's
# lifetime (crash-restart without a volume wipe) is safe.
sed "s|__FLAG__|$FLAG|" /app/seed.sql | db appdb
echo "seeded appdb with flag from $FLAG_SOURCE"

# Run the app as ourselves (ctf) — no setpriv, none allowed here.
# GOTCHA: gunicorn >= 26 starts a control server that writes its socket to
# $HOME/.gunicorn — /home/ctf is on the read-only rootfs under the lab flags.
# Point HOME at the ctf-owned datadir (the VOLUME) so the control server has
# somewhere to write; nothing else in this container uses HOME.
export HOME=/var/lib/mysql
exec gunicorn -b 0.0.0.0:8080 -w 2 app:app
