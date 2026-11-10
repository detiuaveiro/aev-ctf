"""auth1 (NetGuard Router) -- weak/default HTTP Basic credential (OWASP A07).

A cheap home-router admin console gates its status page with HTTP Basic
auth, but ships a weak, never-rotated default credential. The public
landing page requires no auth and carries no secret; only GET /admin --
which answers 401 with no/wrong Basic credentials -- renders the status
page, and only that page shows the "ISP support token" field holding the
flag.

Intended solution: try the shipped default credential (not shown anywhere
in the app or its pages) against /admin's Basic-auth prompt.
"""
import os

from flask import Flask, Response, render_template, request

app = Flask(__name__)

FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def load_flag() -> str:
    # Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag is a read-only
    # directory bind mount of the host's per-challenge flag dir; read /flag/flag PER
    # REQUEST so a rotation after a solve is visible without a restart. (A directory
    # mount, not a file mount: a pinned inode would hide the roller's atomic rename.)
    # The env FLAG (podman secret) is the fallback for local runs with no mount.
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{auth1_local_verify}")

ADMIN_USER = "admin"
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")  # shipped default, never rotated

NAME = "NetGuard Router"
TAGLINE = "Firmware 2.1 · Model NG-220"


def _unauthorized() -> Response:
    return Response(
        "Authentication required.", 401,
        {"WWW-Authenticate": 'Basic realm="NetGuard Router Admin"'},
    )


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/admin")
def admin():
    auth = request.authorization
    if not auth or auth.username != ADMIN_USER or auth.password != ADMIN_PASS:
        return _unauthorized()
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="admin",
                            support_token=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
