"""auth6 (Brightleaf) -- an overbroad cookie scope lets a lower-trust
subdomain plant a session id for the real app (OWASP A07; deck slide 63;
session fixation delivered cross-domain).

Brightleaf runs its marketing microsite and its real app as two vhosts of
the same parent domain, sharing one cookie scoped to that parent --
exactly the deck's "evil.server.com plants a cookie for *.server.com"
scenario. The marketing site (lower trust: anyone can "comment") lets a
visitor set that shared-domain cookie to a value of their choosing. The
real app, on the other vhost, accepts whatever sid arrives as already
valid (strict session handling would reject an unknown id instead) and --
same bug as auth5 -- never rotates it at login.

This single container plays both vhosts by branching on the Host header
(no second DNS name needed for the lab): send Host: marketing.<name> for
the microsite, anything else for the real app.

Intended solution: use the marketing microsite (by Host header) to plant a
chosen sid as the shared-domain cookie, have the registrar's verification
bot sign the manager in under that same sid, then present it to the real
app's dashboard.
"""
import os
import secrets
import time

from flask import Flask, abort, make_response, render_template, request

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
    return os.environ.get("FLAG", "flag{auth6_local_verify}")

NAME = "Brightleaf"
TAGLINE = "Brightleaf App"
MARKETING_TAGLINE = "Brightleaf Marketing"

# sid -> {"authed", "role", "planted_at"}. The sid is student-chosen (that's
# the point of the exercise), which means two different visitors can pick the
# same value -- deliberately or by copying the same example from a lab guide.
# Without an expiry, whoever authenticates a given sid first leaves it
# authenticated for every later visitor who happens to reuse that value,
# forever (this container's process lifetime), letting them skip the actual
# exploit entirely. SESSION_TTL closes that: a sid planted/authenticated more
# than a few minutes ago is treated as gone, so the fixation chain has to be
# (re)run fresh, same as a real attacker would have to beat a session
# lifetime in practice.
SESSIONS: dict[str, dict] = {}
SESSION_TTL = 180  # seconds


def _live(sid: str) -> dict | None:
    s = SESSIONS.get(sid)
    if s and time.time() - s["planted_at"] > SESSION_TTL:
        del SESSIONS[sid]
        return None
    return s


def is_marketing() -> bool:
    return request.host.split(":")[0].startswith("marketing.")


@app.route("/")
def index():
    if is_marketing():
        return render_template("index.html", name=NAME, tagline=MARKETING_TAGLINE,
                                page="marketing-landing")
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/plant", methods=["POST"])
def plant():
    """Marketing microsite only: a "remember me on brightleaf.example"
    comment-form convenience that sets the shared-domain cookie to whatever
    the visitor supplies. On a real second vhost this would be a literal
    Domain=.brightleaf.example cookie; here it's the same bug, scoped to
    this one origin for the lab."""
    if not is_marketing():
        abort(404)
    sid = request.form.get("sid", "").strip()
    if not sid:
        abort(400)
    if not _live(sid):
        SESSIONS[sid] = {"authed": False, "role": None, "planted_at": time.time()}
    resp = make_response("Comment saved.")
    resp.set_cookie("sid", sid)
    return resp


@app.route("/helpdesk/verify-link", methods=["POST"])
def verify_link():
    """Same registrar-style verification bot as the Alma Portal lab (auth5):
    signs the manager account in under a caller-supplied sid, without
    rotating it."""
    if is_marketing():
        abort(404)
    sid = request.form.get("sid", "").strip()
    s = _live(sid)
    if not s:
        abort(400)
    s["authed"] = True
    s["role"] = "manager"
    return "Link verified."


@app.route("/dashboard")
def dashboard():
    """The manager console. Accepts whatever `sid` arrives as already valid
    (strict handling would reject an unknown id) and never rotates it -- the
    fixation half of the bug. The flag is issued only for an authenticated
    *manager* session. When not signed in we still show the visitor their own
    session id: that is the same cookie the marketing microsite can plant, and
    surfacing it is how a student sees the two sites share one session."""
    if is_marketing():
        abort(404)
    sid = request.cookies.get("sid")
    s = _live(sid) if sid else None
    token = load_flag() if (s is not None and s["role"] == "manager") else None
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="dashboard",
                            token=token, sid=sid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
