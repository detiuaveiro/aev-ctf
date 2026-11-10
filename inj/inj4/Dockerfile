# inj4 (Catalogo) -- XXE in the catalogue XML import (Java, unhardened
# DocumentBuilderFactory). Multi-stage: compile with the JDK, run on the JRE.
FROM eclipse-temurin:17-jdk AS build
WORKDIR /src
COPY app/App.java .
RUN javac App.java

FROM eclipse-temurin:17-jre
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
COPY --from=build /src/*.class /app/
USER ctf
EXPOSE 8080
CMD ["java", "-cp", "/app", "App"]
