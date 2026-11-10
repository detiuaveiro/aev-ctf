"""xss3 -- DOM-based XSS: the team card page copies ?card= into innerHTML.

A "team card" builder: /?card=<html> renders a shareable profile card. The
server serves one static page; the browser script copies the card parameter
straight into the card element with innerHTML. No server round-trip, no
stored state -- the sink is client-side, so the reflection never appears in
the response body. The page ships a grant() helper (sets the xss_grant_xss3
cookie, follows to /flag); the flag is granted to any browser whose script
ran it. Intended payload: /?card=<img src=x onerror=grant()>
"""
import os

from flask import Flask, abort, request

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "flag{xss3_local_test}")
# Per-challenge grant cookie: every *.chal.deti name resolves to the same lab
# host and browsers scope cookies by domain+path only (the port is ignored),
# so a shared `xss_grant` cookie earned on one sibling would unlock the others'
# /flag. Naming it per challenge keeps each grant scoped to its own challenge.
GRANT_COOKIE = "xss_grant_xss3"

# One static page for every ?card= value: the parameter is consumed entirely
# in the browser. The default card keeps the page useful without a parameter.
PAGE = """<!doctype html><meta charset=utf-8><title>Team card</title>
<style>
:root{--ink:#241f2e;--mut:#7a7390;--acc:#7c3aed;--bg:#f6f4fb}
*{box-sizing:border-box}
body{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{background:linear-gradient(120deg,#4c1d95,#7c3aed);color:#fff;padding:2.2rem 1.5rem 2.6rem}
header h1{margin:0 0 .3rem;font-size:1.7rem}
header p{margin:0;opacity:.85}
main{max-width:44rem;margin:-1.6rem auto 3rem;padding:0 1rem}
.cardbox{background:#fff;border-radius:.8rem;box-shadow:0 8px 24px rgba(76,29,149,.14);padding:1.4rem 1.5rem}
#card{border:1px solid #e4ddf2;border-radius:.6rem;padding:1rem 1.2rem;min-height:5.5rem;background:#fbfaff}
#card .who{font-weight:700;font-size:1.05rem}
#card .role{color:var(--acc);font-size:.85rem;text-transform:uppercase;letter-spacing:.04em}
#card .bio{color:var(--mut);margin-top:.3rem}
form{display:flex;gap:.6rem;margin-top:1rem}
input[type=text]{flex:1;padding:.7rem .9rem;font:inherit;border:1px solid #d8cff0;border-radius:.6rem}
button{padding:.7rem 1.1rem;font:inherit;font-weight:600;border:0;border-radius:.6rem;background:var(--acc);color:#fff;cursor:pointer}
small{color:var(--mut)}
</style><header><h1>Team card</h1>
<p>Build a shareable profile card. The card lives in the URL, so it can be
sent to anyone.</p></header>
<main><div class="cardbox">
<div id="card"></div>
<form onsubmit="return build()">
<input type="text" id="src" placeholder="Paste card HTML, e.g. <b>Ada</b> &middot; bench lead">
<button>Build</button></form>
<small>The card is rendered by your browser from the <code>card</code> URL
parameter &mdash; the server only ever sends this one page.</small>
</div></main>
<script>
var DEFAULT = '<div class="who">Ada</div><div class="role">bench lead</div>' +
              '<div class="bio">Keeps the oscillosopes honest.</div>';
function render(){
  var c = new URLSearchParams(location.search).get('card');
  // BUG: the parameter is assigned to innerHTML without sanitising.
  document.getElementById('card').innerHTML = c || DEFAULT;
}
function build(){
  var v = document.getElementById('src').value;
  location.search = v ? '?card=' + encodeURIComponent(v) : '';
  return false;
}
function grant(){document.cookie='__GRANT_COOKIE__=1;path=/';location.href='/flag';}
render();
</script>"""
# PAGE is a plain (non-f) string, so splice in the per-challenge cookie name.
PAGE = PAGE.replace("__GRANT_COOKIE__", GRANT_COOKIE)


@app.route("/")
def index():
    # Static by design: the ?card= parameter is never echoed by the server.
    return PAGE


@app.route("/flag")
def flag():
    if request.cookies.get(GRANT_COOKIE) == "1":
        return FLAG
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
