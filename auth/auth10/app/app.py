"""auth10 (PeopleFirst HR) -- user enumeration (CWE-204) chained with a
shared, never-rotated onboarding default password (OWASP A07; deck
slides 45, 48, 54).

Login tells an unknown employee ID ("No such employee ID.") apart from a
known ID with the wrong password ("Incorrect password."). On its own that
only confirms which IDs exist -- it does not read anyone's record. Every
new hire is also handed the SAME onboarding password, and HR never forces a
change. Chaining the two (confirm the ID is real, then try the shared
default) is the actual exploit; only the HR systems administrator's record
carries the flag.

Intended solution: derive candidate employee IDs from the public team
roster (first-initial + last name), confirm the systems administrator's ID
via the login oracle, then authenticate with the shared onboarding default.
"""
import os

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
# Fixed, not per-process: gunicorn runs multiple worker processes (-w 2) and
# each would otherwise mint its own os.urandom() key, so a session cookie
# signed by one worker fails signature verification on another -- random,
# not malicious, cross-worker login flakiness. A fixed key keeps sessions
# valid across workers; it is not the vulnerability under test here.
app.secret_key = os.environ.get("SECRET_KEY", "auth10-fixed-dev-secret-not-for-prod")
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
    return os.environ.get("FLAG", "flag{auth10_local_verify}")

NAME = "PeopleFirst HR"
TAGLINE = "Employee self-service"

DEFAULT_PASSWORD = "admin123"  # shared onboarding default, never forced to rotate

TEAM = [
    ("Priya Natarajan", "HR Systems Administrator"),
    ("Marcus Ebo", "Payroll Specialist"),
    ("Lena Ford", "Recruiter"),
]

USERS = {
    "pnatarajan": {"name": "Priya Natarajan", "role": "HR Systems Administrator",
                   "password": DEFAULT_PASSWORD, "admin": True},
    "mebo": {"name": "Marcus Ebo", "role": "Payroll Specialist",
             "password": "Correct-Horse-7!", "admin": False},
    "lford": {"name": "Lena Ford", "role": "Recruiter",
              "password": "Tr33house#42", "admin": False},
}


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing",
                            team=TEAM)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        emp_id = request.form.get("emp_id", "").strip()
        pw = request.form.get("password", "")
        user = USERS.get(emp_id)
        if user is None:
            error = "No such employee ID."
        elif pw != user["password"]:
            error = "Incorrect password."
        else:
            session["emp_id"] = emp_id
            return redirect(url_for("record"))
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/record")
def record():
    emp_id = session.get("emp_id")
    user = USERS.get(emp_id)
    if not user:
        return redirect(url_for("login"))
    token = load_flag() if user["admin"] else None
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="record",
                            user=user, token=token)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
