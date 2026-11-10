#!/bin/bash
# SQLi template entrypoint (SQLite variant): seed + Flask app, single user.
#
# Runs as a SINGLE fixed user (ctf). The lab runs with DropCapability=ALL +
# read-only rootfs, so there is no privilege drop, no chown, and no DB
# daemon to start: sqlite3 is in-process, and its file lives on the
# /var/lib/app tmpfs (writable under the read-only rootfs; fresh every
# start).
#
# The flag arrives as the live /flag/flag file (lab rolling model; the FLAG
# env — podman secret or local compose — is the fallback when the mount is
# absent) and is interpolated into seed.sql every start. The flag never lives
# in the image.
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

# The DB file lives on the /var/lib/app tmpfs (see challenge.container /
# docker-compose.yml). The tmpfs is fresh on every container start; the
# rm is defensive, and the seed contract (seed.sql uses CREATE TABLE IF NOT
# EXISTS + upsert) makes a re-run safe anyway.
mkdir -p /var/lib/app
rm -f /var/lib/app/app.db
python3 /app/seed.py
echo "seeded /var/lib/app/app.db with flag from $FLAG_SOURCE"

# GOTCHA: gunicorn >= 26 starts a control server that writes its socket to
# $HOME/.gunicorn — /home/ctf is on the read-only rootfs. Point HOME at the
# writable tmpfs; nothing else in this container uses HOME.
export HOME=/var/lib/app

# Run the app as ourselves (ctf) — no setpriv, none allowed here.
exec gunicorn -b 0.0.0.0:8080 -w 2 app:app
