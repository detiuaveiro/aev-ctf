"""auth11 (InboxNow Webmail) -- the password-reset token is a predictable,
non-expiring, reusable function of the account name alone (OWASP A07;
deck slide 54).

A correct reset token is a single-use, short-lived, cryptographically
random value stored hashed server-side, bound to one account. Here it is
`sha256("reset:" + username)` -- the same value every time, for every
account, with no expiry and no per-request randomness at all. Knowing the
target's address (InboxNow's own "contact the postmaster" footer names
one) is enough to compute their reset token directly -- the forgot-
password *form* doesn't even need to be used.

Intended solution: read the postmaster's address off the public footer,
compute its reset token, and use /reset/<token> to set a new password for
that mailbox.
"""
import hashlib
import os

from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "auth11-fixed-dev-secret-not-for-prod")
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
    return os.environ.get("FLAG", "flag{auth11_local_verify}")

NAME = "InboxNow Webmail"
TAGLINE = "Email, simplified"

MAILBOXES = {
    "user": {"password": "user123", "inbox": ["Welcome to InboxNow!"]},
    "postmaster": {"password": os.urandom(16).hex(), "inbox": None},  # filled per request from load_flag()
}


def reset_token(username: str) -> str:
    return hashlib.sha256(f"reset:{username}".encode()).hexdigest()[:20]


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing",
                            user=session.get("user"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        box = MAILBOXES.get(u)
        if box and box["password"] == p:
            session["user"] = u
            return redirect(url_for("mailbox"))
        error = "Invalid credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/mailbox")
def mailbox():
    u = session.get("user")
    box = MAILBOXES.get(u)
    if not box:
        return redirect(url_for("login"))
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="mailbox",
                            mails=(box["inbox"] if box["inbox"] is not None else [load_flag()]))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    sent = None
    if request.method == "POST":
        u = request.form.get("username", "")
        if u in MAILBOXES:
            # A real app would email the link to that address. In this test
            # environment the mailbox is unreachable, so the link is rendered
            # into the page but hidden (display: none) — the visible response
            # is only "a reset link has been sent to your email address".
            sent = f"/reset/{reset_token(u)}"
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="forgot",
                            sent=sent)


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    target = next((u for u in MAILBOXES if reset_token(u) == token), None)
    if not target:
        abort(404)
    if request.method == "POST":
        MAILBOXES[target]["password"] = request.form.get("password", "")
        session["user"] = target
        return redirect(url_for("mailbox"))
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="reset",
                            token=token)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
