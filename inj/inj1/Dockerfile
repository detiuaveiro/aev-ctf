# inj1 (LibraryNet) -- OS command injection in the OPAC node health check.
FROM python:3.12-slim
RUN pip install --no-cache-dir flask gunicorn \
    && apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*
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
# Decoy: the "secret" the developer thought they hid in the app config.
# The real flag is /flag/flag (live mount), reachable only through the shell.
RUN printf 'API_URL="http://opac.internal"\nFLAG="flag{decoy_this_is_not_it}"\n' > /app/config.env
EXPOSE 8080
USER ctf
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app:app"]
