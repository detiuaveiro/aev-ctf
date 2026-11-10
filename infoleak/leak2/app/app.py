"""leak2 (formerly leak-debug-endpoint) -- a hidden debug route leaks the environment.

A route /debug/env is registered behind a trivial obfuscation. It returns
os.environ, which includes FLAG. The route should have been gated behind a
feature flag or removed for production.

Intended solution: find and call /debug/env, read the flag from the dump.
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)
FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def load_flag() -> str:
    # Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag/flag
    # is a read-only bind mount of the host flag file, read PER REQUEST so a
    # rotation is visible without a restart. The env FLAG (podman secret) is
    # the fallback for local/docker-compose runs where no mount exists.
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{debug_endpoint_local}")


@app.route("/")
def index():
    return ("<h1>App</h1><p>Normal API service.</p>"
        '<small>status: <a href="/status">/status</a></small>')


@app.route("/api/ping")
def ping():
    return jsonify({"ok": True})


# Hidden debug route. Disabled in 'production' but someone left it enabled.
@app.route("/debug/env")
def debug_env():
    env = {k: v for k, v in os.environ.items()}
    # The env FLAG is fixed at container start (podman secret); in the lab the
    # live flag is the /flag/flag mount, so refresh it for the dump.
    env["FLAG"] = load_flag()
    return jsonify(env)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
