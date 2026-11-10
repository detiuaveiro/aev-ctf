"""leak4 (formerly leak-git) -- an exposed .git directory leaks a commit message.

The app serves the repository root, including .git, as static files. The flag
was committed early on and the file removed later, but the initial commit
message -- which contained the flag -- is still recorded in .git/logs/HEAD.

Intended solution: fetch /.git/logs/HEAD and read the flag from the message.

NOTE: this flag is fixed in the git history at image-build time, not injected
per student via FLAG. The FLAG env is ignored for this challenge.
"""
import os
from flask import Flask, send_from_directory

app = Flask(__name__)

ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return ("<h1>Build host</h1><p>Release v1.4.2</p>"
        '<a href="/CHANGELOG.md">changelog</a>')


@app.route("/<path:name>")
def files(name):
    if not name:
        return index()
    return send_from_directory(ROOT, name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
