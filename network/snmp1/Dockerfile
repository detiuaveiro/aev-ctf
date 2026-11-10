FROM python:3.12-slim

RUN useradd -m -u 1000 ctf

WORKDIR /app
COPY app/ .

USER ctf
EXPOSE 161/udp
# UDP SNMPv2c agent (stdlib only, no flask/gunicorn); FLAG injected at deploy
# time via the podman secret -> env.
CMD ["python", "-u", "app.py"]
