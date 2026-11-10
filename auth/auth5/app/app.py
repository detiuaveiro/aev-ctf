"""auth5 (Alma Portal) -- session fixation: the session identifier is not
rotated at login (OWASP A07; deck slides 60-62; CWE-384).

Every visitor gets a browsing session id before ever logging in (so guest
browsing of the public catalog has *some* state). The bug: logging in
keeps using that SAME id -- it is never regenerated. If an attacker can get
a victim to authenticate while using an id the attacker already knows (a
"check this course link" message is the classic delivery -- the deck's own
slides 60-62 scenario), the attacker can then use that same id themselves,
now authenticated as the victim.

This single-container lab has no second human, so a "registrar verification
bot" stands in for the victim: it is a real feature some ticketing systems
have (automatically opening a link to confirm it works) and, driven with an
attacker-chosen session id, it reproduces exactly the slide's scenario:
the id is fixed before the bot's login, and stays valid after.

Intended solution: mint your own pre-login sid (visit /), hand that sid to
the verification bot so it logs the advisor in under it, then reuse the
same sid against /dashboard.
"""
import os
import secrets

from flask import Flask, abort, make_response, redirect, render_template, request, url_for

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
    return os.environ.get("FLAG", "flag{auth5_local_verify}")

NAME = "Alma Portal"
TAGLINE = "University student & staff portal"

# sid -> {"authed": bool, "role": str | None}. In-process only (single
# gunicorn worker -- see Dockerfile) since this is the whole point under
# test: the SAME sid that existed before login is still valid after.
SESSIONS: dict[str, dict] = {}


def get_or_create_sid() -> str:
    sid = request.cookies.get("sid")
    if sid and sid in SESSIONS:
        return sid
    sid = secrets.token_hex(16)
    SESSIONS[sid] = {"authed": False, "role": None}
    return sid


@app.route("/")
def index():
    sid = get_or_create_sid()
    resp = make_response(render_template("index.html", name=NAME, tagline=TAGLINE,
                                          page="landing", sid=sid))
    resp.set_cookie("sid", sid)
    return resp


@app.route("/helpdesk/verify-link", methods=["POST"])
def verify_link():
    """The registrar's "verify a shared link" bot: used when a student
    forwards a ticket saying a portal link is broken. The form on the
    landing page posts the link, and the bot opens it *as the caller's own
    session* (the sid cookie that travels with the request), then signs in
    with the advisor's own SSO button to confirm the page loads for staff.
    It does not rotate the sid on sign-in -- the bug under test: the
    caller's pre-login session comes back authenticated as the advisor.
    """
    sid = request.cookies.get("sid", "")
    if sid not in SESSIONS:
        abort(400)
    SESSIONS[sid]["authed"] = True
    SESSIONS[sid]["role"] = "advisor"
    return "Link verified."


@app.route("/dashboard")
def dashboard():
    sid = request.cookies.get("sid")
    s = SESSIONS.get(sid)
    if not s or not s["authed"]:
        return redirect(url_for("index"))
    token = load_flag() if s["role"] == "advisor" else None
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="dashboard",
                            token=token)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
