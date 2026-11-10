"""leak1 (formerly leak-backup-file) -- an orphaned .bak file leaks the flag.

The developer edited config.py with an editor that left config.py.bak behind.
The real config.py carries no secret; the backup still holds the flag. The
developer only thought to hide config.py, not its backup.

Intended solution: discover and fetch /static/config.py.bak.
"""
import os
from flask import Flask, abort

# Disable Flask's built-in /static/ handler so OUR /static/<path:name> route
# (which serves the orphaned backup) is the one that answers.
app = Flask(__name__, static_folder=None)
FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def load_flag() -> str:
    # Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag is a
    # read-only bind mount of the host's per-challenge flag directory; the
    # app reads /flag/flag PER REQUEST so a rotation is visible without a
    # restart. (A directory mount, not a file mount: a bind mount pins the
    # file's inode, so an atomic tmp+rename of a directly-mounted file would
    # be invisible to the container.) The env FLAG (podman secret) is the
    # fallback for local/docker-compose runs where no mount exists.
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{backup_local}")


CONFIG = "API_URL = 'https://api.acme.internal'\n"


@app.route("/")
def index():
    return ("<h1>App</h1><p>Static assets under /static/.</p>"
        '<a href="/static/config.py">config</a>')


@app.route("/static/<path:name>")
def static_(name):
    if name == "config.py":
        return CONFIG
    if name == "config.py.bak":
        return f"API_URL = 'https://api.acme.internal'\nFLAG = '{load_flag()}'\n"
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
