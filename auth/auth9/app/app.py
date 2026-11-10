"""auth9 (DeskHero Helpdesk) -- session tokens derived from a predictable
timestamp (OWASP A07; deck slide 59; CWE-330/331).

Every login mints a token as sha1(f"{username}:{unix_timestamp}") --
convenient, deterministic, and exactly the "bad pattern" the deck calls
out: the timestamp is guessable to within a couple of seconds, so the
token's real entropy is tiny. The on-call rotation service re-authenticates
its admin integration account on every refresh tick; an attacker who
triggers a refresh and knows roughly when it happened can recompute the
token for every timestamp in that narrow window and simply try each one.

Intended solution: trigger an on-call refresh, note the local time, then
brute-force the token over a few seconds around it.
"""
import hashlib
import os
import time

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
    return os.environ.get("FLAG", "flag{auth9_local_verify}")

NAME = "DeskHero Helpdesk"
TAGLINE = "IT ticketing, for humans"

AGENTS = {"agent": "agent123"}

# token -> username. In-process only (single worker -- see Dockerfile).
TOKENS: dict[str, str] = {}

# Display-only fake queue data for the agent console.
TICKETS = [
    ("DH-1042", "Printer on 3F spits out smoke", "open"),
    ("DH-1041", "VPN login loops in Safari", "open"),
    ("DH-1039", "Password reset for J. Weiss", "solved"),
    ("DH-1035", "Monitor flickers in the dark room", "solved"),
]
ONCALL = "M. Okafor"

# Timestamp of the last on-call rotation (0 = none yet). In-process,
# single worker -- see Dockerfile.
LAST_ROTATION = 0


def issue_token(username: str) -> str:
    t = int(time.time())
    token = hashlib.sha1(f"{username}:{t}".encode()).hexdigest()
    TOKENS[token] = username
    return token


@app.route("/")
def index():
    last = (time.strftime("%H:%M:%S", time.localtime(LAST_ROTATION))
            if LAST_ROTATION else None)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing",
                           oncall=ONCALL, last_rotation=last)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if AGENTS.get(u) == p:
            token = issue_token(u)
            resp = make_response(redirect(url_for("queue")))
            resp.set_cookie("token", token)
            return resp
        error = "Invalid credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


def _render_queue(user: str, flash: str | None):
    last = (time.strftime("%H:%M:%S", time.localtime(LAST_ROTATION))
            if LAST_ROTATION else None)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="queue",
                           user=user, tickets=TICKETS, oncall=ONCALL,
                           last_rotation=last, flash=flash)


@app.route("/queue")
def queue():
    user = TOKENS.get(request.cookies.get("token", ""))
    if not user:
        return redirect(url_for("login"))
    return _render_queue(user, None)


@app.route("/bot/refresh-oncall", methods=["POST"])
def refresh_oncall():
    """Simulates the on-call rotation service re-authenticating the admin
    integration account on every refresh tick. The resulting token is never
    returned to the caller -- only its existence (and the fact that it was
    just minted, at the current timestamp) is implied. A signed-in agent gets
    the agent console back with a confirmation; a headless caller gets the
    plain-text ack."""
    global LAST_ROTATION
    issue_token("admin")
    LAST_ROTATION = int(time.time())
    user = TOKENS.get(request.cookies.get("token", ""))
    if user:
        return _render_queue(user, "On-call rotation refreshed — the new on-call agent has signed in.")
    return "on-call rotation refreshed"


@app.route("/ticket/admin")
def admin_ticket():
    token = request.cookies.get("token")
    user = TOKENS.get(token)
    if user != "admin":
        abort(403)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="ticket",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
