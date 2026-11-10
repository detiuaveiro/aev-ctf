"""auth12 (Cornerstone CMS) -- a credential store is reachable in a
reversible/cleartext form through an exposed export path (OWASP A07;
deck slides 46, 49; CWE-257/CWE-522).

An old "staging export" of the CMS database was left published at a
predictable static path. It holds the admin account's password encoded
with base64 and labelled "encrypted" in a comment -- base64 is an
encoding, not encryption (deck slide 24 makes the same point about HTTP
Basic auth). The export itself carries no flag -- only the admin
credential. The flag only appears on the admin-only CMS dashboard, reached
by actually logging in with that recovered credential.

Nothing on the real site links to the export -- it is only discoverable
the way a genuinely forgotten artifact would be: a `robots.txt` entry
telling crawlers not to index the folder (advisory only, same lesson as
the infoleak suite's leak8 -- Disallow is a courtesy to crawlers, not
access control), and the folder itself left with directory listing
enabled, the way a web server with autoindex on would actually render it.
"""
import base64
import os

from flask import Flask, abort, redirect, render_template, request, session, url_for

ROBOTS_TXT = "User-agent: *\nDisallow: /export/\n"

# What a real forgotten export folder would actually contain: the backup
# that matters, plus a couple of ordinary neighbours -- an autoindex lists
# everything in the directory, not just the interesting file.
EXPORT_FILES = ["cornerstone_staging.sql.bak", ".htaccess", "README.txt"]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "auth12-fixed-dev-secret-not-for-prod")
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
    return os.environ.get("FLAG", "flag{auth12_local_verify}")

NAME = "Cornerstone CMS"
TAGLINE = "Content, managed"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or base64.b64encode(os.urandom(9)).decode()
USERS = {"admin": ADMIN_PASSWORD}

BACKUP_SQL = f"""-- cornerstone_staging export, 2021-11-02
-- NOTE: password column is "encrypted" (base64) at rest.
INSERT INTO cms_users (username, password_encrypted) VALUES
  ('admin', '{base64.b64encode(ADMIN_PASSWORD.encode()).decode()}');
"""


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/robots.txt")
def robots():
    return ROBOTS_TXT, 200, {"Content-Type": "text/plain"}


@app.route("/export/")
def export_listing():
    # A bare, unstyled autoindex -- this is the web server listing a
    # directory it was never configured to hide, not a page the CMS itself
    # renders. No logo, no nav: it looks exactly as out of place as a
    # forgotten artifact should.
    rows = "".join(f'<li><a href="/export/{n}">{n}</a></li>' for n in EXPORT_FILES)
    return f"<h1>Index of /export/</h1><ul>{rows}</ul>", 200, {"Content-Type": "text/html"}


@app.route("/export/<path:name>")
def export_file(name):
    if name == "cornerstone_staging.sql.bak":
        return BACKUP_SQL, 200, {"Content-Type": "text/plain"}
    if name == ".htaccess":
        return "Options -Indexes\n", 200, {"Content-Type": "text/plain"}
    if name == "README.txt":
        return "Staging exports -- clean up after each migration.\n", 200, {"Content-Type": "text/plain"}
    abort(404)


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
    if session.get("user") != "admin":
        return redirect(url_for("login"))
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="dashboard",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
