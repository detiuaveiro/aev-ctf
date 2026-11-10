"""leak10 (formerly leak-verbose-error) -- verbose stack-trace information disclosure.

The /crash route raises an exception after stashing the flag in a local
variable. A blanket error handler returns the raw Python traceback, which
includes the frame's local variables -- including our secret.

Intended solution: request /crash and read the flag from the traceback.
"""
import os
import traceback
from flask import Flask, request

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
    return os.environ.get("FLAG", "flag{verbose_error_local}")


@app.route("/")
def index():
    return ("<h1>Error lab</h1>"
        '<form action="/crash" method="get">' +
        '<input name="msg"><button>send</button></form>')


@app.route("/crash")
def crash():
    secret = load_flag()   # leaked via traceback frame locals (read live)
    raise RuntimeError(f"boom in {request.path}")


@app.errorhandler(Exception)
def on_error(e):
    # Verbose: dump the full traceback WITH frame locals to the client.
    tb = traceback.TracebackException.from_exception(e, capture_locals=True)
    return "<pre>" + "".join(tb.format()) + "</pre>", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
