"""leak6 (formerly leak-jwt) -- the app signs a JWT whose payload carries the flag.

A /login endpoint returns a (barely) signed JWT. The developer put the flag in
the payload as a 'feature flag' so the client could toggle UI -- a secret
stuffed into a token that the client can trivially decode.

Intended solution: log in, decode the JWT payload, read the flag.
"""
import os
import base64
import json
import hmac
import hashlib
from flask import Flask, jsonify

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
    return os.environ.get("FLAG", "flag{jwt_payload_local}")


SECRET = os.environ.get("JWT_SECRET", "insecure-dev-secret")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_token(sub: str) -> str:
    header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64url(json.dumps({
        "sub": sub, "role": "user", "feature_flags": {"show_admin": True},
        "flag": load_flag(),
    }).encode())
    signing = f"{header}.{payload}".encode()
    sig = b64url(hmac.new(SECRET.encode(), signing, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


@app.route("/")
def index():
    return ("<h1>Auth service</h1>"
        '<form action="/login" method="post">' +
        '<input name="user" value="guest"><button>login</button></form>')


@app.route("/login", methods=["POST"])
def login():
    return jsonify({"token": make_token("guest")})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
