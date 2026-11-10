# wordpress — stock WordPress 6.9.4, vulnerable to "wp2shell":
#   CVE-2026-63030 (REST batch/v1 endpoint route confusion) +
#   CVE-2026-60137 (WP_Query author__not_in not sanitised)
#   => unauthenticated SQLi -> admin account forgery -> arbitrary command
#      execution. Fixed in 6.8.6 / 6.9.5 / 7.0.2; 6.9.4 is the last vulnerable
#      6.9.x and the version the public PoC validates against.
#
# Single container (stock wordpress image + in-container MariaDB + wp-cli) so
# it fits the lab's one-Quadlet-unit-per-challenge model (D-58: no compose on
# the host). The lab builds it locally as localhost/lab/wordpress:latest;
# challenge.container is the Quadlet unit the lab-challenge helper installs.
#
# The flag is NOT baked in: lab-challenge injects it at deploy time as the
# FLAG env (a podman secret), and entrypoint.sh materializes it to
# /etc/lab_flag (outside the web root). The DB user gets the stock
# ALL ON wordpress.* grant only (no FILE privilege), so the SQLi alone cannot
# read files — the RCE is required to recover the flag.
FROM docker.io/library/wordpress:6.9.4

# MariaDB for the single-container model, wget for wp-cli.
RUN apt-get update && apt-get install -y --no-install-recommends \
        mariadb-server mariadb-client wget \
    && rm -rf /var/lib/apt/lists/*

# wp-cli for the scripted, idempotent install (the stock image no longer
# auto-installs: its entrypoint only copies the tree and generates
# wp-config.php from WORDPRESS_* env).
RUN set -eux; \
    wget -qO /usr/local/bin/wp \
        "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"; \
    chmod +x /usr/local/bin/wp

# The stock wp-config.php (generated from wp-config-docker.php) reads its DB
# settings from these env vars AT RUNTIME (getenv_docker). They must be
# container-level ENV — not just entrypoint exports — or any process that does
# not inherit the entrypoint's shell (podman exec, cron, wp-cli) connects to
# the image's defaults (host 'db', user 'wordpress') and fails.
ENV WORDPRESS_DB_HOST=127.0.0.1 \
    WORDPRESS_DB_NAME=wordpress \
    WORDPRESS_DB_USER=wp \
    WORDPRESS_DB_PASSWORD=wppass

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# WordPress serves on 80 inside the container (published as 8084 in the lab).
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apache2-foreground"]
