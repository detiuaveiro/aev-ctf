"""leak8 (formerly leak-robots) -- flag hidden behind a robots.txt disallowed path.

/robots.txt advertises a directory that robots must not crawl: /admin-secret/.
The directory is publicly served and contains the flag. The 'security' here is
purely 'do not index it', which is no security at all.

Intended solution: read /robots.txt, then fetch the disallowed path.
"""
import os
from flask import Flask

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "flag{robots_local}")

ROBOTS = "User-agent: *\nDisallow: /admin-secret/\n"


@app.route("/")
def index():
    return ("<h1>Public site</h1><p>Nothing interesting.</p>"
        '<small>crawlers: see our rules' +
        '<br><img src="/favicon.ico" width="1" height="1"></small>')


@app.route("/robots.txt")
def robots():
    return ROBOTS, 200, {"Content-Type": "text/plain"}


@app.route("/admin-secret/")
def secret():
    return f"<pre>{FLAG}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
