"""auth7 (ConnectAPI Partner Gateway) -- JWT verification accepts "alg":
"none" (OWASP A07; deck slides 42-43, 56).

Partners log in and get a signed (HS256) JWT identifying which partner
they are. The verifier decides HOW to check the signature by reading the
token's OWN "alg" header -- so a token that claims "alg": "none" skips
signature verification entirely. The server must pin the expected
algorithm itself and never let the token choose.

A JWT is just three base64url parts (header.payload.signature); this app
implements the handful of lines it needs with the stdlib (hmac/hashlib/
base64/json) rather than pulling in a dependency.

Intended solution: log in as the seeded (non-admin) partner to see the
token shape, then craft a token with header {"alg":"none"} and payload
{"partner":"admin"}, signature left empty.
"""
import base64
import hashlib
import hmac
import json
import os
import time

from flask import Flask, abort, make_response, render_template, request

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
    return os.environ.get("FLAG", "flag{auth7_local_verify}")
# Fixed per-process -- see Dockerfile (single worker): signing and
# verification must agree, and there's no external store for this lab.
SECRET = os.environ.get("JWT_SECRET", "connectapi-signing-secret-not-for-prod")

NAME = "ConnectAPI Partner Gateway"
TAGLINE = "B2B integration console"

PARTNERS = {"acme": "acmepass"}


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def issue_token(partner: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"partner": partner, "iat": int(time.time())}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"


def verify_token(token: str) -> dict | None:
    try:
        h_b64, p_b64, s_b64 = token.split(".")
        header = json.loads(_b64url_decode(h_b64))
        payload = json.loads(_b64url_decode(p_b64))
    except Exception:
        return None
    alg = header.get("alg")
    if alg == "none":
        # BUG: the token picked its own algorithm, and we believed it.
        return payload
    if alg == "HS256":
        expected = hmac.new(SECRET.encode(), f"{h_b64}.{p_b64}".encode(),
                             hashlib.sha256).digest()
        try:
            actual = _b64url_decode(s_b64)
        except Exception:
            return None
        if hmac.compare_digest(expected, actual):
            return payload
    return None


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("partner", "")
        p = request.form.get("secret", "")
        if PARTNERS.get(u) == p:
            resp = make_response(render_template("index.html", name=NAME, tagline=TAGLINE,
                                                   page="issued", token=issue_token(u)))
            return resp
        error = "Invalid partner credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/partner/admin")
def partner_admin():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    payload = verify_token(token)
    if not payload or payload.get("partner") != "admin":
        abort(403)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="admin",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
