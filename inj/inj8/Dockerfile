# inj8 (StockEye) -- OS command injection via a blacklist that forgets the glob.
FROM php:8.3-cli
# Ensure UID/GID 1000 exists as "ctf"; if the base image already owns UID 1000
# (e.g. ubuntu in temurin, node in node:slim) rename that account instead.
RUN set -eu; \
    if getent passwd 1000 >/dev/null 2>&1; then \
        oldu="$(getent passwd 1000 | cut -d: -f1)"; \
        if [ "$oldu" != "ctf" ]; then \
            oldg="$(getent group 1000 | cut -d: -f1)"; \
            groupmod -n ctf "$oldg"; \
            usermod -l ctf "$oldu"; \
        fi; \
    else \
        useradd -m -u 1000 ctf; \
    fi; \
    id ctf
WORKDIR /app
COPY app/server.php ./
# A file the audit legitimately inspects (gives the tool a real job).
RUN printf 'sku,stock,row\nA1-042,14,Fiction Row 4\nB2-101,6,SciFi Row 2\n' > /app/inventory.csv \
    && chown -R ctf:ctf /app
USER ctf
EXPOSE 8080
CMD ["php", "-S", "0.0.0.0:8080", "server.php"]
