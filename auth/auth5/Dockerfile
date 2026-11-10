FROM python:3.12-slim

RUN pip install --no-cache-dir flask gunicorn && \
    useradd -m -u 1000 ctf

WORKDIR /app
COPY app/ .

USER ctf
EXPOSE 8080
# Single worker: SESSIONS is in-process state (no external store), and
# that's exactly what's under test here -- the sid itself, not a signed
# cookie -- so it must not be split across worker processes.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "app:app"]
