"""xss1 -- reflected XSS: the recipe search echoes the query back unescaped.

A small "lab recipe" search box. /?q=<term> filters the corpus and renders
`Results for <q>` -- <q> is interpolated straight into the HTML (and into the
input's value attribute). The page ships a grant() helper that sets the
xss_grant_xss1 cookie and follows to /flag; the flag is granted to any browser
whose script ran it. Intended payload: <img src=x onerror=grant()>
"""
import os

from flask import Flask, abort, request

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "flag{xss1_local_test}")
# Per-challenge grant cookie: every *.chal.deti name resolves to the same lab
# host and browsers scope cookies by domain+path only (the port is ignored),
# so a shared `xss_grant` cookie earned on one sibling would unlock the others'
# /flag. Naming it per challenge keeps each grant scoped to its own challenge.
GRANT_COOKIE = "xss_grant_xss1"

RECIPES = [
    ("Salt bridge", "Melt a salt pill across a 9V cell for a quick spark."),
    ("Coffee filter", "Fold a paper coffee filter into a four-ply face mask."),
    ("Baking soda fire", "Smother a small oil fire with baking soda, never water."),
    ("Static cling", "Rub a balloon on wool; lift paper scraps with the charge."),
    ("Magnet test", "Distinguish steel from aluminium with a fridge magnet."),
    ("Buzzer trick", "A 9V cell plus a piezo buzzer makes a loud chirp."),
]

CSS = """
:root{--ink:#1c2430;--mut:#6b7686;--acc:#2563eb;--bg:#f4f6fb}
*{box-sizing:border-box}
body{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{background:linear-gradient(120deg,#1e3a8a,#2563eb);color:#fff;padding:2.2rem 1.5rem 2.6rem}
header h1{margin:0 0 .3rem;font-size:1.7rem}
header p{margin:0;opacity:.85}
main{max-width:44rem;margin:-1.6rem auto 3rem;padding:0 1rem}
.card{background:#fff;border-radius:.8rem;box-shadow:0 8px 24px rgba(30,58,138,.12);padding:1.4rem 1.5rem}
form{display:flex;gap:.6rem}
input[type=search]{flex:1;padding:.7rem .9rem;font:inherit;border:1px solid #cdd6e4;border-radius:.6rem}
button{padding:.7rem 1.1rem;font:inherit;font-weight:600;border:0;border-radius:.6rem;background:var(--acc);color:#fff;cursor:pointer}
.q{margin:1.2rem 0 .4rem;font-weight:600;color:var(--acc)}
ul{list-style:none;padding:0;margin:0}
li{padding:.55rem 0;border-bottom:1px solid #edf1f7}
li b{display:block}
li span{color:var(--mut);font-size:.92rem}
.empty{color:var(--mut);padding:.8rem 0}
"""


def page(q: str, results: str) -> str:
    return f"""<!doctype html><meta charset=utf-8><title>Lab recipes</title>
<style>{CSS}</style><header><h1>Lab recipes</h1>
<p>Small tricks from the workshop bench. Search to find one.</p></header>
<main><div class="card">
<form action="/" method="get">
<input type="search" name="q" placeholder="Search recipes..." value="{q}">
<button>Search</button></form>
{results}
</div></main>
<script>function grant(){{document.cookie='{GRANT_COOKIE}=1;path=/';location.href='/flag';}}</script>"""


@app.route("/")
def index():
    q = request.args.get("q", "")
    if not q:
        results = '<p class="empty">Try "salt", "magnet" or "buzzer".</p>'
    else:
        hits = [r for r in RECIPES if q.lower() in (r[0] + " " + r[1]).lower()]
        # BUG: q is interpolated into HTML without escaping (twice, even).
        if hits:
            items = "".join(f"<li><b>{t}</b><span>{b}</span></li>" for t, b in hits)
            results = f'<div class="q">Results for {q}</div><ul>{items}</ul>'
        else:
            results = (f'<div class="q">Results for {q}</div>'
                       '<p class="empty">Nothing matches.</p>')
    return page(q, results)


@app.route("/flag")
def flag():
    if request.cookies.get(GRANT_COOKIE) == "1":
        return FLAG
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
