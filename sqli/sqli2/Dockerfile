# SQLi suite base image: Flask app + embedded MariaDB in one container.
# One container keeps the corpus contract (1 challenge = 1 image = 1 Quadlet
# unit = 1 flag secret); uniform MySQL dialect across all 8 challenges.
#
# Hardening note: the lab runs these with DropCapability=ALL + read-only
# rootfs, which strips CAP_SETUID / CAP_CHOWN / CAP_DAC_OVERRIDE. So the
# container CANNOT drop privileges or chown at runtime — it runs as a single
# fixed user (ctf, below) and the DB is fully provisioned at BUILD time
# (datadir + 'app' DB user + empty appdb), persisted in a VOLUME so the
# runtime only ever starts the server and loads the seeded data.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends mariadb-server \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask gunicorn requests pymysql \
    && useradd -m -u 1000 ctf

# Build-time DB provisioning (runs as root, full privileges — the only place
# we have them). Creates the 'app' DB user (ALL on appdb.* + FILE, loopback
# use) and an empty appdb, then hands the datadir to ctf so the runtime user
# can write it. The datadir is a VOLUME (see below): at runtime podman copies
# it from the image into a writable volume on first start, so this
# provisioning survives the read-only rootfs.
RUN set -eux; \
    install -d -m 2745 -o mysql -g mysql /run/mysqld; \
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql; \
    mariadbd --user=mysql --datadir=/var/lib/mysql --bind-address=127.0.0.1 --skip-log-bin & \
    server_pid=$!; \
    for i in $(seq 1 60); do \
        mysqladmin --socket=/run/mysqld/mysqld.sock ping >/dev/null 2>&1 && break; \
        kill -0 "$server_pid" 2>/dev/null || { echo "mariadbd died during build provisioning"; exit 1; }; \
        sleep 1; \
    done; \
    mysql --socket=/run/mysqld/mysqld.sock -e "CREATE DATABASE IF NOT EXISTS appdb; CREATE USER 'app'@'%' IDENTIFIED BY 'apppass'; GRANT ALL PRIVILEGES ON appdb.* TO 'app'@'%'; GRANT FILE ON *.* TO 'app'@'%'; FLUSH PRIVILEGES;"; \
    mysqladmin --socket=/run/mysqld/mysqld.sock shutdown; \
    wait "$server_pid" || true; \
    chown -R ctf:ctf /var/lib/mysql

WORKDIR /app
# COPY app/ .  =>  /app/app.py, /app/templates/, /app/static/  (gunicorn
# runs "app:app": the Flask `app` object in the module /app/app.py).
COPY app/ .
COPY seed.sql entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Writable, persists the build-time provisioning across the read-only rootfs.
VOLUME /var/lib/mysql

EXPOSE 8080
USER ctf
ENTRYPOINT ["/app/entrypoint.sh"]
