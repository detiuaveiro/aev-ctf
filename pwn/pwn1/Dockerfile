# Build the binary against a pinned libc, then serve it over TCP with socat.
# Pinning the base image is what makes stack offsets reproducible everywhere.
#
# socat is used here because it is transparent and passes FLAG straight through
# to the child, which keeps this example runnable in CI with zero ceremony.
# For a graded deployment, swap the runtime stage for pwn.red/jail (nsjail) --
# see solution/README.md -- to get per-connection isolation and resource limits.
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libc6-dev make socat && rm -rf /var/lib/apt/lists/*

# Unprivileged user to run the service.
RUN useradd -m -u 1000 ctf

WORKDIR /src
COPY src/ .
# Intentionally weak build -- this is the point of the challenge.
RUN gcc -fno-stack-protector -no-pie -O0 -w -o /home/ctf/vuln vuln.c \
    && chmod 755 /home/ctf/vuln

USER ctf
WORKDIR /home/ctf

# FLAG is injected per student at deploy time (docker run -e FLAG=flag{...});
# socat exports the container env into each connection's process.
EXPOSE 9001
CMD ["socat", "-T60", "TCP-LISTEN:9001,reuseaddr,fork", "EXEC:./vuln,stderr"]
