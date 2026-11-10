FROM python:3.12-slim

RUN pip install --no-cache-dir flask gunicorn && \
    useradd -m -u 1000 ctf && \
    apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ .

# Build the git history the challenge leaks: the flag is committed early, then
# removed. It survives in .git/logs/HEAD (commit message) and the object store.
RUN git init -q && \
    git config user.email dev@acme.internal && \
    git config user.name dev && \
    printf 'flag{g1t_h1story_l34ks}\n' > flag.txt && \
    git add flag.txt && \
    git commit -q -m "temp: add flag flag{g1t_h1story_l34ks} for testing" && \
    git rm -q flag.txt && \
    git commit -q -m "chore: remove temp flag"

USER ctf
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "app:app"]
