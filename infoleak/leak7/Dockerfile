FROM python:3.12-slim

RUN pip install --no-cache-dir flask gunicorn && \
    useradd -m -u 1000 ctf

WORKDIR /app
COPY app/ .

USER ctf
EXPOSE 8080
# gunicorn for a realistic multi-worker service; FLAG injected at deploy time.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app:app"]
