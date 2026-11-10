"""auth13 (RemoteLink VPN) -- no rate limiting on login, and the seeded
account has a low-entropy password (OWASP A07; deck slides 45, 47, 51).

Online guessing is only impractical if it's slowed down or capped; this
login endpoint accepts unlimited attempts, as fast as a client can send
them, with no per-account or per-IP throttling. The seeded account's
password is drawn from a small, common set -- short dictionary attack,
no lockout to stop it.
"""
import os

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "auth13-fixed-dev-secret-not-for-prod")
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
    return os.environ.get("FLAG", "flag{auth13_local_verify}")

NAME = "RemoteLink VPN"
TAGLINE = "Remote access, simplified"

# One of the most-used passwords in the world (a keyboard pattern, not the
# literal word "password") -- the point under test is the absence of rate
# limiting, not a truly unguessable secret.
VPNUSER_PASSWORD = os.environ.get("VPNUSER_PASSWORD", "qwerty")
USERS = {"vpnuser": VPNUSER_PASSWORD}


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if USERS.get(u) == p:
            session["user"] = u
            return redirect(url_for("dashboard"))
        error = "Invalid credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="dashboard",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
