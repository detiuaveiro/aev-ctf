"""inj13 (FaaSDeck) -- command injection behind "sandboxing" filters.

The platform sells isolation and ships two guards that look right:

  1. POST /functions  deploys a function. The body must be a pipeline of
     allowlisted text filters (tr, sort, wc, ...) with no shell
     metacharacters. A body that reads files is rejected, so the deploy door
     is NOT the way in.
     POST /invoke     runs it:  sh -c "echo <input> | <body>"
     The input is checked for  ; | &  and the word "flag" -- but it is still
     pasted into a shell command line, so  $(...)  and backticks run.

  2. POST /exec       cluster exec (kubectl exec style). The pod is allowlisted
     and so is the command (ls, cat, ps, env, id, df), and  ; | &  and the
     word "flag" are refused. The args are then joined into
         sh -c "cd /app && <args>"
     so command substitution still runs.

The app never reads /flag/flag; the injected shell does. Note: the live
/flag mount is a 0711 root-owned directory (by lab design, so its contents
can't be enumerated) -- a glob like /f*/f* needs readdir permission the ctf
uid does not have, and fails there even though cat-by-exact-name works. The
bypass has to build the literal path without ever writing the word "flag" in
the HTTP request, not by wildcarding around it.

Intended solution (either door; the point is the filter bypass):
    exec:    pod=web-1,
             args="cat /$(printf %b '\\146\\154\\141\\147')/$(printf %b '\\146\\154\\141\\147')"
             (octal-escaped "flag" built at shell-execution time, never
             appears as that literal substring in the request)
    invoke:  deploy name=up body="head -n 5";
             input="$(cat /$(printf %b '\\146\\154\\141\\147')/$(printf %b '\\146\\154\\141\\147'))"
"""
import json
import os
import re
import subprocess

from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FaaSDeck</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#eef1fb;--ac:#4f46e5;--ac2:#e0e7ff;--hd:linear-gradient(90deg,#1e1b4b,#4f46e5);--line:#d3d8f0;--code:#0f172a;--codeink:#a5f3fc}</style></head><body><header><span class="logo">☁️</span><div><b>FaaSDeck</b><small>Serverless functions &amp; cluster exec</small></div><nav><a href="/">Console</a></nav></header><main>"""
_TAIL = """</main><footer>FaaSDeck · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
STORE = "/tmp/functions.json"
PODS = ["web-1", "api-1", "worker-1"]
NAME_RE = re.compile(r"^[a-z0-9_-]+$")
FILTERS = {"tr", "sort", "uniq", "wc", "head", "tail", "rev", "tac", "cut", "base64"}
EXEC_CMDS = {"ls", "cat", "ps", "env", "id", "df"}
BODY_BAD = re.compile(r"[;&$`<>()\\\n]")
LOOSE_BAD = re.compile(r"[;|&]|flag", re.I)


def body_ok(body):
    """Deploy-time check: a pipeline of allowlisted filters, no metacharacters
    other than the pipe (strict, and correct -- this door is closed)."""
    if BODY_BAD.search(body):
        return False
    stages = [st.split() for st in body.split("|")]
    return all(st and st[0] in FILTERS for st in stages)


def exec_ok(args):
    """Exec-time check: allowlisted command, no ; | & and no word "flag".
    Looks like a filter; does not stop $(...), backticks or globs."""
    return args.split()[0] in EXEC_CMDS and not LOOSE_BAD.search(args)


def load():
    try:
        with open(STORE) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save(fn):
    with open(STORE, "w") as fh:
        json.dump(fn, fh)


@app.route("/")
def index():
    fns = load()
    items = "".join(f"<li>{n}: <code>{b}</code></li>" for n, b in fns.items())
    return page(
        "<h1>Function Platform</h1>"
        "<p>Deploy a function, invoke it, or exec into a pod. "
        "Each function runs in its own isolated environment.</p>"
        '<h2>Deploy</h2>'
        '<form action="/functions" method="post">'
        '<label>name <input name="name" value="health"></label> '
        '<label>body <input name="body" size="48" value="tr a-z A-Z"></label> '
        "<button>🚀 deploy</button></form>"
        '<h2>Invoke</h2>'
        '<form action="/invoke" method="post">'
        '<label>function <input name="name" value="health"></label> '
        '<label>input <input name="input" value="x"></label> '
        "<button>⚡ invoke</button></form>"
        '<h2>Cluster exec</h2>'
        '<form action="/exec" method="post">'
        '<label>pod <select name="pod">'
        + "".join(f"<option>{p}</option>" for p in PODS) + "</select></label> "
        '<label>args <input name="args" size="40" value="ls"></label> '
        "<button>exec</button></form>"
        f"<h2>Deployed functions</h2><div class='card'><ul>{items or '<li>(none)</li>'}</ul></div>")


@app.route("/functions", methods=["POST"])
def functions():
    name = request.form.get("name", "")
    body = request.form.get("body", "")
    if not NAME_RE.match(name):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>name may only use a-z 0-9 _ -</p></div>"), 400
    if not body.strip():
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>body must not be empty</p></div>"), 400
    if not body_ok(body):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>body must be a pipeline of: "
                    + ", ".join(sorted(FILTERS)) + "</p></div>"), 400
    fn = load()
    fn[name] = body
    save(fn)
    return page(f"<h1>Deployed</h1><div class='card'><p>function {name} deployed.</p></div>"
                "<a class='back' href='/'>← back</a>")


@app.route("/invoke", methods=["POST"])
def invoke():
    name = request.form.get("name", "")
    inp = request.form.get("input", "")
    body = load().get(name)
    if body is None:
        return page(f"<h1>Not found</h1><div class='card'><p class='bad'>no such function: {name}</p></div>"), 404
    if LOOSE_BAD.search(inp):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>input contains blocked characters</p></div>"), 400
    try:
        out = subprocess.run(
            f"echo {inp} | {body}", shell=True,
            capture_output=True, text=True, timeout=10)
        text = (out.stdout + out.stderr).strip() or "(no output)"
    except Exception as e:
        text = f"error: {e}"
    return page(f"<h1>invoke {name}</h1><pre>{text}</pre><a class='back' href='/'>← back</a>")


@app.route("/exec", methods=["POST"])
def exec_():
    pod = request.form.get("pod", "")
    args = request.form.get("args", "").strip()
    if pod not in PODS:
        return page(f"<h1>Rejected</h1><div class='card'><p class='bad'>unknown pod: {pod}</p></div>"), 400
    if not args:
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>args must not be empty</p></div>"), 400
    if not exec_ok(args):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>command not permitted</p></div>"), 400
    try:
        out = subprocess.run(
            f"cd /app && {args}", shell=True,
            capture_output=True, text=True, timeout=10)
        text = (out.stdout + out.stderr).strip() or "(no output)"
    except Exception as e:
        text = f"error: {e}"
    return page(f"<h1>exec {pod}</h1><pre>{text}</pre><a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
