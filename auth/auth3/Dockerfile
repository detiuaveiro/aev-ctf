FROM python:3.12-slim

RUN pip install --no-cache-dir flask gunicorn && \
    useradd -m -u 1000 ctf

WORKDIR /app
COPY app/ .

USER ctf
EXPOSE 8080
# Single worker: the VIP/guest sid map is in-process state, not shared
# across workers (and doesn't need to be -- it's fixed at process start).
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "1", "app:app"]
