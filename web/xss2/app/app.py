"""xss2 -- stored XSS: bench log entries are rendered unescaped for everyone.

A small "bench log" where lab members leave notes for the next shift. Entries
are appended to an in-memory list and rendered into the page for every visitor
without escaping. The page ships a grant() helper (sets the xss_grant_xss2 cookie,
follows to /flag); the flag is granted to any browser whose script ran it.
Intended payload (as the note text): <img src=x onerror=grant()>
"""
import os

from flask import Flask, abort, redirect, request, url_for

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "flag{xss2_local_test}")
# Per-challenge grant cookie: every *.chal.deti name resolves to the same lab
# host and browsers scope cookies by domain+path only (the port is ignored),
# so a shared `xss_grant` cookie earned on one sibling would unlock the others'
# /flag. Naming it per challenge keeps each grant scoped to its own challenge.
GRANT_COOKIE = "xss_grant_xss2"

# author -> text; the log is shared by every shift.
NOTES = [
    ("marta", "Calibrated the oscilloscope; probe 2 was 0.8% slow."),
    ("jonas", "Ordered new alligator clips — the red ones finally gave up."),
    ("marta", "Left the soldering station on, do not touch the iron."),
]

CSS = """
:root{--ink:#20242b;--mut:#69707d;--acc:#0f766e;--bg:#f2f7f6}
*{box-sizing:border-box}
body{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{background:linear-gradient(120deg,#134e4a,#0f766e);color:#fff;padding:2.2rem 1.5rem 2.6rem}
header h1{margin:0 0 .3rem;font-size:1.7rem}
header p{margin:0;opacity:.85}
main{max-width:44rem;margin:-1.6rem auto 3rem;padding:0 1rem}
.card{background:#fff;border-radius:.8rem;box-shadow:0 8px 24px rgba(19,78,74,.12);padding:1.4rem 1.5rem}
form{display:grid;grid-template-columns:1fr;gap:.6rem;margin-bottom:1.2rem}
input[type=text],textarea{padding:.7rem .9rem;font:inherit;border:1px solid #c9d8d5;border-radius:.6rem}
textarea{min-height:4.2rem;resize:vertical}
button{justify-self:start;padding:.7rem 1.1rem;font:inherit;font-weight:600;border:0;border-radius:.6rem;background:var(--acc);color:#fff;cursor:pointer}
h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;color:var(--mut);margin:0 0 .6rem}
li{list-style:none;padding:.6rem 0;border-bottom:1px solid #edf3f2}
li b{color:var(--acc);margin-right:.4rem}
ul{padding:0;margin:0}
"""


def page(entries: str) -> str:
    return f"""<!doctype html><meta charset=utf-8><title>Bench log</title>
<style>{CSS}</style><header><h1>Bench log</h1>
<p>Leave a note for the next shift. Everyone on the bench reads it.</p></header>
<main><div class="card">
<form action="/log" method="post">
<input type="text" name="author" placeholder="Your name" required maxlength=40>
<textarea name="text" placeholder="What should the next shift know?" required maxlength=280></textarea>
<button>Add note</button>
</form>
<h2>Recent notes</h2><ul>{entries}</ul>
</div></main>
<script>function grant(){{document.cookie='{GRANT_COOKIE}=1;path=/';location.href='/flag';}}</script>"""


@app.route("/")
def index():
    # BUG: author and text are interpolated into HTML without escaping.
    entries = "".join(f"<li><b>{a}</b>{t}</li>" for a, t in NOTES[-12:])
    return page(entries)


@app.route("/log", methods=["POST"])
def log():
    author = (request.form.get("author") or "").strip()[:40]
    text = (request.form.get("text") or "").strip()[:280]
    if author and text:
        NOTES.append((author, text))
    return redirect(url_for("index"))


@app.route("/flag")
def flag():
    if request.cookies.get(GRANT_COOKIE) == "1":
        return FLAG
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
