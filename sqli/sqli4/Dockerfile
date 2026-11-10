# SQLi challenge template — SQLite variant (DEFAULT).
#
# One container = Flask app + SQLite database (stdlib sqlite3; there is no
# DB server process). App and DB file run as the SAME fixed user (ctf),
# which matters because the lab runs challenges with DropCapability=ALL +
# read-only rootfs (no setuid, no chown, no daemon tricks). The database
# file lives on a /var/lib/app tmpfs mount (writable under the read-only
# rootfs) and is re-seeded from the FLAG env every start.
#
# Use templates/sqli-mysql only for challenges whose technique needs
# MySQL-specific mechanics: updatexml (error-based), SLEEP (time-based),
# INTO OUTFILE (OOB write).
FROM python:3.12-slim
RUN pip install --no-cache-dir flask gunicorn requests \
    && useradd -m -u 1000 ctf
WORKDIR /app
# gunicorn runs "app:app" → the module must be /app/app.py (COPY app/ .,
# NOT ./app/ — that nests to /app/app/app.py and fails to load).
COPY app/ .
COPY seed.sql seed.py entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
EXPOSE 8080
USER ctf
ENTRYPOINT ["/app/entrypoint.sh"]
