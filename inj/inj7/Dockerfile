# inj7 (DeskOne) -- OS command injection through the ticket log line.
FROM python:3.12-slim
RUN pip install --no-cache-dir flask gunicorn
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
COPY app/ .
EXPOSE 8080
USER ctf
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app:app"]
