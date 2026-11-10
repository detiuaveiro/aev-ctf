"""auth8 (PocketBank Lite) -- JWTs signed with a short, guessable HMAC
secret (OWASP A07; deck slides 42, 56).

The signature check itself is correct (HS256 only, no "alg": "none" hole --
contrast with auth7). The flaw is the secret: a 4-digit numeric PIN-style
string, small enough to brute-force completely offline against one sample
token in well under a second, then reuse to forge a token for any account.

Intended solution: log in as the seeded customer (the issued token comes
back in a `token` cookie, not on the page), brute-force the 4-digit secret
against its signature, then forge a token with role=admin signed with the
recovered secret.
"""
import base64
import hashlib
import hmac
import json
import os
import random
import time

from flask import Flask, abort, make_response, redirect, render_template, request, url_for

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
    return os.environ.get("FLAG", "flag{auth8_local_verify}")

NAME = "PocketBank Lite"
TAGLINE = "Mobile banking, in your browser"

CUSTOMERS = {"customer": "customer123"}

# Display-only fake account data for the post-login dashboard.
ACCOUNTS = {
    "customer": {
        "name": "Alex Rivera",
        "account": "•••• 4821",
        "balance": "$1,284.37",
        "transactions": [
            ("Oct 28", "Grocery run — Corner Market", "−$42.10"),
            ("Oct 25", "Salary — Northwind Studio", "+$2,450.00"),
            ("Oct 24", "Streaming bundle", "−$18.99"),
            ("Oct 23", "Coffee — Daily Grind", "−$4.75"),
        ],
    },
}

# A 4-digit numeric secret -- small enough to brute-force completely.
# Regenerated every process start (not hardcoded) so the exploit has to
# actually crack it, not just know it. Fixed per-process -- see Dockerfile
# (single worker): signing and verification must agree.
SECRET = os.environ.get("JWT_SECRET") or f"{random.randint(0, 9999):04d}"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def issue_token(account: str, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"account": account, "role": role, "iat": int(time.time())}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(SECRET.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"


def verify_token(token: str) -> dict | None:
    try:
        h_b64, p_b64, s_b64 = token.split(".")
        header = json.loads(_b64url_decode(h_b64))
        payload = json.loads(_b64url_decode(p_b64))
        actual = _b64url_decode(s_b64)
    except Exception:
        return None
    if header.get("alg") != "HS256":
        return None
    expected = hmac.new(SECRET.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
    if hmac.compare_digest(expected, actual):
        return payload
    return None


@app.route("/")
def index():
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="landing")


def _render_dashboard(account: str):
    holder = ACCOUNTS.get(account) or {"name": account, "account": "•••• 0000",
                                        "balance": "$0.00", "transactions": []}
    return render_template("index.html", name=NAME, tagline=TAGLINE,
                           page="dashboard", holder=holder)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("account", "")
        p = request.form.get("password", "")
        if CUSTOMERS.get(u) == p:
            token = issue_token(u, "customer")
            # The token goes into a cookie; the page shows only the (fake)
            # dashboard, so a client must read the token from Set-Cookie /
            # its cookie jar.
            resp = make_response(_render_dashboard(u))
            resp.set_cookie("token", token, path="/", samesite="Lax")
            return resp
        error = "Invalid account credentials."
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="login",
                            error=error)


@app.route("/dashboard")
def dashboard():
    token = request.cookies.get("token")
    payload = verify_token(token) if token else None
    if not payload:
        return redirect(url_for("index"))
    return _render_dashboard(payload.get("account", "customer"))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("token", path="/")
    return resp


@app.route("/accounts/admin")
def accounts_admin():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() or request.cookies.get("token", "")
    payload = verify_token(token)
    if not payload or payload.get("role") != "admin":
        abort(403)
    return render_template("index.html", name=NAME, tagline=TAGLINE, page="admin",
                            flag=load_flag())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
