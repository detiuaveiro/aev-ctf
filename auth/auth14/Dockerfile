FROM python:3.12-slim

RUN pip install --no-cache-dir flask gunicorn && \
    useradd -m -u 1000 ctf

WORKDIR /app
COPY app/ .

USER ctf
EXPOSE 8080
# Single worker: SESSIONS/DIAGNOSTICS_LOG are in-process state -- see
# auth5's Dockerfile note.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "app:app"]
