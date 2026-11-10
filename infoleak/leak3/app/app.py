"""leak3 (formerly leak-dir-listing) -- enabled directory listing reveals a flag file.

/public/ is served with directory listing enabled (an intentional misconfig).
One of the listed files, flag.txt, holds the per-student flag.

Intended solution: list /public/, see flag.txt, fetch it.
"""
import os
from flask import Flask, abort

app = Flask(__name__)
FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def load_flag() -> str:
    # Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag is a
    # read-only bind mount of the host's per-challenge flag directory; the
    # app reads /flag/flag PER REQUEST so a rotation is visible without a
    # restart. The env FLAG (podman secret) is the fallback for
    # local/docker-compose runs where no mount exists.
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{dir_listing_local}")


# In-memory files served under /public/. flag.txt holds the secret (read live
# per request; the entry is a placeholder so the listing stays stable).
FILES = {"readme.txt": "nothing to see here\n", "flag.txt": ""}


@app.route("/")
def index():
    return ("<h1>Media</h1><p>Company media hub.</p>"
                '<img src="/public/banner.png" alt="banner">')


@app.route("/public/")
def listing():
    links = "".join(
        f'<li><a href="/public/{n}">{n}</a></li>' for n in FILES)
    return f"<h2>Index of /public/</h2><ul>{links}</ul>"


@app.route("/public/<path:name>")
def file_(name):
    if name == "flag.txt":
        return load_flag() + "\n"
    if name in FILES:
        return FILES[name]
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
