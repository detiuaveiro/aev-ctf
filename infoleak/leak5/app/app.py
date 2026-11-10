"""leak5 (formerly leak-idor-api) -- API enumeration + verbose serialization leak.

Users are addressable by sequential id at /api/users/<id>. The admin's id is
leaked in a JavaScript bundle (/static/app.js). A hidden query parameter
`verbose=true` makes the serializer include every field -- including the flag
that should stay server-side.

Intended solution: read the JS to learn the admin id, then request that id
with verbose=true to get the flag.
"""
import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)
FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def load_flag() -> str:
    # Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag is a
    # read-only bind mount of the host's per-challenge flag directory; the
    # app reads /flag/flag PER REQUEST so a rotation is visible without a
    # restart. The env FLAG (podman secret) is the fallback for
    # local/docker-compose runs where no mount exists.
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{idor_api_local}")


ADMIN_ID = 7
USERS = {
    1: {"id": 1, "username": "alice", "email": "alice@example.com"},
    2: {"id": 2, "username": "bob", "email": "bob@example.com"},
    3: {"id": 3, "username": "carol", "email": "carol@example.com"},
    4: {"id": 4, "username": "dave", "email": "dave@example.com"},
    5: {"id": 5, "username": "erin", "email": "erin@example.com"},
    6: {"id": 6, "username": "frank", "email": "frank@example.com"},
    7: {"id": 7, "username": "admin", "email": "admin@example.com",
        "role": "admin", "flag": None},
}
JS = "// profile viewer\nconst ADMIN_PROFILE_ID = 7;\n// loadProfile(ADMIN_PROFILE_ID);\n"


def serialize(user: dict, verbose: bool) -> dict:
    fields = ["id", "username", "email"]
    if verbose:
        fields = list(user.keys())   # includes role and flag
    return {k: user[k] for k in fields if k in user}


@app.route("/")
def index():
    return ("<h1>API</h1><p>Directory service.</p>"
        '<a href="/api/users/1">profile</a>')


@app.route("/static/app.js")
def js():
    return JS, 200, {"Content-Type": "application/javascript"}


@app.route("/api/users/<int:uid>")
def user(uid):
    u = USERS.get(uid)
    if not u:
        return jsonify({"error": "not found"}), 404
    if "flag" in u:
        # The admin record's flag is read live (rolling flag), not cached at
        # import time.
        u = {**u, "flag": load_flag()}
    verbose = request.args.get("verbose", "").lower() in ("1", "true", "yes")
    return jsonify(serialize(u, verbose))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
