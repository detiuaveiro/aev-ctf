"""auth4 (ExpenseFlow) -- the server trusts a client-controlled role value
(OWASP A07; deck slide 19, "Anything can be a client" / slide 5's point that
control must live server-side).

Logging in sets two things: a real server-side session (who you are) AND a
plain, readable `role` cookie the server (wrongly) ALSO trusts to decide
whether to allow /manager -- instead of checking the role it actually
recorded for this session at login. The "Manager console" link on the
employee's own dashboard is a real, always-visible nav link (no JS hiding
it), exactly like a real internal tool's nav bar would show it: an
employee can see the manager area exists and even click through to it --
they just get refused once they're there, same as any normal app. The
seeded employee account's own role cookie says "employee", so that refusal
is correct -- until the cookie is edited directly.

Intended solution: log in with the seeded employee account, then request
/manager with the `role` cookie changed to `manager` (no new credential
needed -- the session is still the employee's).
"""
import os

from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "auth4-fixed-dev-secret-not-for-prod")
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
    return os.environ.get("FLAG", "flag{auth4_local_verify}")

NAME = "ExpenseFlow"
TAGLINE = "Expense reports, approved fast"

USERS = {"employee": {"password": "employee123", "role": "employee"}}

MAX_EXPENSES = 20  # keep each session's own list bounded


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing",
                            user=session.get("user"), expenses=session.get("expenses", []))


@app.route("/expenses", methods=["POST"])
def add_expense():
    """Employees submit their own reports; each session only ever sees its
    own list (stored in the signed session cookie, not a shared dict) --
    this is ordinary app functionality, not the vulnerability under test."""
    if "user" not in session:
        return redirect(url_for("login"))
    description = request.form.get("description", "").strip()[:120]
    try:
        value = round(float(request.form.get("value", "0")), 2)
    except ValueError:
        value = 0.0
    if description and value > 0:
        expenses = session.get("expenses", [])
        expenses.append({"description": description, "value": value})
        session["expenses"] = expenses[-MAX_EXPENSES:]
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        user = USERS.get(u)
        if user and user["password"] == p:
            session["user"] = u
            resp = redirect(url_for("index"))
            # Readable AND writable by the client -- the bug is that
            # /manager trusts this cookie instead of session["user"]'s
            # real, server-recorded role.
            resp.set_cookie("role", user["role"])
            return resp
        error = "Invalid credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/manager")
def manager():
    if "user" not in session:
        return redirect(url_for("login"))
    role = request.cookies.get("role")
    if role != "manager":
        abort(403)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="manager",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
