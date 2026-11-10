"""leak9 (formerly leak-source-comment) -- an information-disclosure challenge.

The home page renders an empty-looking page, but the HTML source carries a
comment that leaks the flag. The developer left a `<!-- FLAG: ... -->` marker
in the template for 'debugging' and never removed it.

Intended solution: view the page source and read the comment.
"""
import os
from flask import Flask

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
    return os.environ.get("FLAG", "flag{source_comment_local}")


def render_page() -> str:
    # Built per request (not at import time) so the leaked comment always
    # carries the CURRENT flag after a rotation.
    return f"""<!DOCTYPE html>
<html>
<head><title>Acme Corp</title></head>
<body>
  <!-- TODO: remove this debug marker before shipping -->
  <!-- FLAG: {load_flag()} -->
  <h1>Welcome to Acme Corp</h1>
  <p>Nothing to see here. Please move along.</p>
  <button>edit</button>
</body>
</html>
"""


@app.route("/")
def index():
    return render_page()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
