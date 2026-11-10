"""leak7 (formerly leak-oracle) -- a prefix oracle leaks the flag character by character.

/oracle?prefix=<s> returns 200 if <s> is a prefix of FLAG, else 403. It reveals
a single bit of information per request, letting a client reconstruct the whole
flag. The flag charset is [a-z0-9{}_].

Intended solution: iteratively guess each character by testing prefixes.
"""
import os
from flask import Flask, request, abort

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
    return os.environ.get("FLAG", "flag{oracle_local}")


@app.route("/")
def index():
    return ("<h1>Oracle</h1>"
        '<form action="/oracle" method="get">' +
        '<input name="prefix"><button>check</button></form>')


@app.route("/oracle")
def oracle():
    prefix = request.args.get("prefix", "")
    if load_flag().startswith(prefix):
        return "yes"
    abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
