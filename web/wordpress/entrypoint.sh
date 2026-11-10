#!/bin/bash
# wordpress challenge entrypoint (wp2shell target).
#
# Brings up MariaDB in-container, installs stock WordPress 6.9.4
# (vulnerable to the wp2shell chain: CVE-2026-63030 + CVE-2026-60137)
# idempotently, ensures one published post exists (the exploit needs a
# public post permalink as its oEmbed seed URL), materializes the injected
# FLAG outside the web root, then serves with Apache. The container's main
# process is Apache (exec at the end); MariaDB runs in the background.
set -euo pipefail

DB=wordpress
DBUSER=wp
DBPASS=wppass
# The site's own DNS name, on purpose: the exploit's oEmbed seed flow makes
# WordPress fetch its own post URLs via wp_safe_remote_get, and only same-host
# URLs skip WP's private-IP block. wordpress.chal.deti resolves (wildcard
# *.chal.deti) from inside the container to the lab-services host, and the
# hairpin back through published port 8084 reaches this container. Using the
# DNS name also keeps every rendered link/redirect on the address students
# actually use — siteurl=http://127.0.0.1 made WordPress 301 the front page
# onto the student's own localhost.
WP_URL="${WP_URL:-http://wordpress.chal.deti:8084}"

# --- 1. MariaDB -------------------------------------------------------------
mkdir -p /run/mysqld
chown -R mysql:mysql /run/mysqld /var/lib/mysql
if [ ! -d /var/lib/mysql/mysql ]; then
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql >/dev/null
fi
mysqld --user=mysql --datadir=/var/lib/mysql >/var/log/mysqld.log 2>&1 &

# Wait until the server answers (root connects via the unix socket; the
# entrypoint runs as the root OS user, so unix_socket auth is enough).
for _ in $(seq 1 60); do
    mysqladmin --user=root ping >/dev/null 2>&1 && break
    sleep 0.5
done
if ! mysqladmin --user=root ping >/dev/null 2>&1; then
    echo "entrypoint: MariaDB failed to start" >&2
    cat /var/log/mysqld.log >&2 || true
    exit 1
fi

# --- 2. Database + application user ----------------------------------------
# Stock wordpress-image grant: ALL ON wordpress.* only — deliberately NO
# FILE privilege, so a read-only SQLi cannot reach /etc/lab_flag.
mysql --user=root <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB}\`;
CREATE USER IF NOT EXISTS '${DBUSER}'@'localhost' IDENTIFIED BY '${DBPASS}';
GRANT ALL PRIVILEGES ON \`${DB}\`.* TO '${DBUSER}'@'localhost';
FLUSH PRIVILEGES;
SQL

# --- 3. WordPress -----------------------------------------------------------
# wp-config.php is generated from wp-config-docker.php, which reads its DB
# settings from the WORDPRESS_* env (Dockerfile ENV) at runtime; wp-cli then
# creates tables, the admin user, and the post.
cd /var/www/html
# The stock image ships the tree in /usr/src/wordpress and copies it into the
# webroot from its entrypoint — but only when invoked as apache2*/php-fpm, so
# we do the copy (and the wp-config generation from WORDPRESS_* env) ourselves.
if [ ! -e index.php ] && [ ! -e wp-includes/version.php ]; then
    chown -R www-data:www-data /var/www/html
    tar --create --file - --directory /usr/src/wordpress \
        --owner www-data --group www-data . | tar --extract --file -
fi
if [ ! -s wp-config.php ]; then
    awk '
        /put your unique phrase here/ {
            cmd = "head -c1m /dev/urandom | sha1sum | cut -d\\  -f1"
            cmd | getline str
            close(cmd)
            gsub("put your unique phrase here", str)
        }
        { print }
    ' /usr/src/wordpress/wp-config-docker.php > wp-config.php
    chown www-data:www-data wp-config.php
fi

# wp-cli refuses to run as root; the web tree belongs to www-data.
if ! su -s /bin/bash www-data -c "wp --quiet core is-installed" 2>/dev/null; then
    su -s /bin/bash www-data -c "
        wp --quiet core install \
            --url='$WP_URL' \
            --title='The Quiet Blog' \
            --admin_user=admin --admin_password=admin --admin_email=admin@example.com
    "
fi
# A published post (idempotent): the exploit fetches the first published
# post's permalink and uses it as the oEmbed seed base URL.
if [ -z "$(su -s /bin/bash www-data -c 'wp --quiet post list --post_status=publish --field=ID 2>/dev/null' | head -1)" ]; then
    su -s /bin/bash www-data -c "
        wp --quiet post create \
            --post_title='Notes from the garden' \
            --post_content='The roses came in early this year. Nothing else to report.' \
            --post_status=publish --post_author=1
    "
fi

# --- 4. Materialize the flag OUTSIDE the web root ---------------------------
# In the lab, /flag/flag is a read-only bind mount of the host flag file --
# the LIVE source (a rotation rewrites it atomically; no restart). It is
# exposed as /etc/lab_flag (where the solution's RCE reads) via a symlink so
# every read follows the live file. It is never baked into the image, and no
# HTTP route or SQLi can reach it, so the RCE is required to recover it.
# For local/docker-compose runs (no /flag mount) fall back to the injected
# FLAG env, as before.
if [ -r /flag/flag ]; then
    ln -sf /flag/flag /etc/lab_flag
elif [ -n "${FLAG:-}" ]; then
    printf '%s' "$FLAG" > /etc/lab_flag
    chmod 644 /etc/lab_flag
fi

# --- 5. Serve ---------------------------------------------------------------
exec apache2-foreground
