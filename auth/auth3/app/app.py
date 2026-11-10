"""auth3 (QuickShip Tracker) -- session identifier carried in the URL
(OWASP A07; deck slides 29-30, 37).

Tracking links mailed to customers embed their parcel's token in the URL
(?sid=...). URLs leak -- into browser history, server logs, and anywhere
they get copy-pasted. Here, a support agent pasted a VIP customer's full
tracking link into a public "customer stories" page while writing up a
testimonial, so that customer's sid (and the concierge token behind it) is
sitting in plain public text. No login exists in this app at all -- the sid
in the URL *is* the only credential -- and the regular, non-VIP tracking
link that a tester starts from never carries one.

Intended solution: read the leaked tracking link out of /stories, then
request /track with that sid.
"""
import os
import secrets

from flask import Flask, render_template, request

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
    return os.environ.get("FLAG", "flag{auth3_local_verify}")

NAME = "QuickShip Tracker"
TAGLINE = "Where's my parcel?"

VIP_SID = secrets.token_hex(8)
GUEST_SID = secrets.token_hex(8)

PARCELS = {
    GUEST_SID: {"customer": "J. Alvarez", "status": "Out for delivery", "vip": False},
    VIP_SID: {"customer": "R. Okafor", "status": "Out for delivery", "vip": True},
}

STORY_HTML = (
    "<p>\"My package arrived early! The support agent even sent me a direct "
    f"link so I could keep an eye on it: "
    f"<code>/track?sid={VIP_SID}</code>. Five stars.\" &mdash; R. Okafor "
    "(verified VIP customer)</p>"
)


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing",
                            guest_sid=GUEST_SID)


@app.route("/stories")
def stories():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="stories",
                            story=STORY_HTML)


@app.route("/track")
def track():
    sid = request.args.get("sid", "")
    parcel = PARCELS.get(sid)
    if not parcel:
        return render_template("index.html", name=NAME, tagline=TAGLINE, page="notfound")
    token = load_flag() if parcel["vip"] else None
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="track",
                            parcel=parcel, token=token)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
