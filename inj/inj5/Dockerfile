# inj5 (NightPack) -- OS command injection in the backup one-liner (Go).
FROM golang:1.22-bookworm AS build
WORKDIR /src
COPY app/go.mod app/main.go ./
RUN CGO_ENABLED=0 go build -o /out/nightpack .

FROM debian:bookworm-slim
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
COPY --from=build /out/nightpack /app/nightpack
# The directory the backup legitimately packs (gives the tool a real job).
RUN mkdir -p /app/catalog \
    && printf 'sku,name,row\nA1-042,Fiction Row 4\nB2-101,SciFi Row 2\n' > /app/catalog/products.csv \
    && chown -R ctf:ctf /app
USER ctf
EXPOSE 8080
CMD ["/app/nightpack"]
