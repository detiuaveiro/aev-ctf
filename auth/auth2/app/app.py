"""auth2 (Harbor Wiki) -- access control trusts the client-supplied Referer
header (OWASP A07; CWE-293).

The internal ops runbook page is only supposed to be reachable by staff who
navigated there from the staff home page -- but the check inspects the
Referer header the client sends, not a real session or role. The header is
entirely client-controlled: it can be forged on a direct request, with no
staff session and without ever visiting the staff home page.

Intended solution: GET /wiki/internal/ops-runbook with a forged Referer
header pointing at /wiki/staff-home.
"""
import os

from flask import Flask, abort, render_template, request

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
    return os.environ.get("FLAG", "flag{auth2_local_verify}")

NAME = "Harbor Wiki"
TAGLINE = "Team knowledge base"
STAFF_HOME = "/wiki/staff-home"
RUNBOOK = "/wiki/internal/ops-runbook"


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route(STAFF_HOME)
def staff_home():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="staff-home")


@app.route(RUNBOOK)
def ops_runbook():
    referer = request.headers.get("Referer", "")
    if STAFF_HOME not in referer:
        abort(403)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="runbook",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
