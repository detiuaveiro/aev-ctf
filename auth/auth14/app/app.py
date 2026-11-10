"""auth14 (FernBank Online) -- logout clears only the client-side cookie;
the server-side session stays valid (OWASP A07; deck slide 64; CWE-613 --
insufficient session expiration).

A monitoring probe signs the branch manager in each night to pull the
shift report, then "logs out" -- which, same bug a real customer would
hit, only ever clears the cookie it was holding, never the server-side
session record. The probe's own session id ends up logged on the public
ops diagnostics page (a separate, smaller flaw: verbose debug logging --
but the point under test is that even a correctly-*found* stale id should
have been useless after logout, and it isn't).

Intended solution: trigger the probe, read its session id off the public
diagnostics page, and present it directly to the dashboard -- after the
probe has already "logged out".
"""
import os
import secrets
import time

from flask import Flask, g, redirect, render_template, request, url_for

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
    return os.environ.get("FLAG", "flag{auth14_local_verify}")

NAME = "FernBank Online"
TAGLINE = "Online banking console"

# sid -> {"role": str, "logged_out": bool}. In-process only -- see Dockerfile.
SESSIONS: dict[str, dict] = {}
DIAGNOSTICS_LOG: list[dict] = []

# Every visitor is signed in as an ordinary customer: a missing or unknown
# sid cookie mints a fresh low-privilege session. This is what makes the
# pivot visible -- students hold their OWN session id (shown on their
# dashboard), then swap it for the manager's id found via the probe's
# diagnostics trace. Customer sessions never see the manager token/flag.
CUSTOMER_ROLE = "customer"
SESSION_CAP = 500  # trim oldest anonymous sessions; dict is insertion-ordered


@app.before_request
def ensure_session():
    sid = request.cookies.get("sid")
    if sid is not None and sid in SESSIONS:
        g.sid = sid
        g.new_sid = None
        return
    sid = secrets.token_hex(16)
    SESSIONS[sid] = {"role": CUSTOMER_ROLE, "logged_out": False}
    while len(SESSIONS) > SESSION_CAP:
        del SESSIONS[next(iter(SESSIONS))]
    g.sid = sid
    g.new_sid = sid  # after_request hands the fresh id back as a cookie


@app.after_request
def issue_session_cookie(resp):
    if getattr(g, "new_sid", None):
        resp.set_cookie("sid", g.new_sid, httponly=True, samesite="Lax")
    return resp


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/bot/manager-shift-report", methods=["POST"])
def manager_shift_report():
    """Nightly monitoring probe: signs the branch manager in, pulls the
    shift report, then "logs out". The logout only ever discards the
    probe's own cookie -- the session record below is never invalidated,
    which is the bug under test. The resulting sid is written only to the
    internal diagnostics trace, not returned here. Branch staff can also
    trigger it manually from the landing page's "Run shift report sync"
    button, which POSTs here."""
    sid = secrets.token_hex(16)
    SESSIONS[sid] = {"role": "manager", "logged_out": False}
    # "Log out": the probe discards its own cookie. Nothing server-side
    # changes -- SESSIONS[sid] stays valid. (A correct logout would mark
    # it invalid here.)
    DIAGNOSTICS_LOG.append({"ts": time.strftime("%H:%M:%S"), "sid": sid,
                             "note": "manager shift-report probe, session closed by client"})
    DIAGNOSTICS_LOG[:] = DIAGNOSTICS_LOG[-20:]
    return "shift report complete"


@app.route("/diagnostics")
def diagnostics():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="diagnostics",
                            log=DIAGNOSTICS_LOG)


@app.route("/dashboard")
def dashboard():
    s = SESSIONS.get(g.sid)
    if not s:
        # Should not happen (before_request mints a session), but never 500.
        return redirect(url_for("index"))
    token = load_flag() if s["role"] == "manager" else None
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="dashboard",
                            token=token, sid=g.sid, role=s["role"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
