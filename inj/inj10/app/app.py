"""inj10 (ToolDesk) -- command override via a user-controlled PATH prefix.

The dashboard runs its diagnostics through a shell:
    sh -c "PATH=/tmp/plugins:$PATH <tool>"
so that uploaded "plugins" (small scripts) can shadow the stock tools. The
plugin NAME and the tool name are sanitized to [A-Za-z0-9._-] and the tool
must be a known plugin -- but the CONTENT of an uploaded plugin is code, and
a plugin named `sysdiag` wins PATH resolution over the stock one. The flag
is /flag/flag, read by the shadowed plugin at run time.

Intended solution: upload a plugin named `sysdiag` that cats /flag/flag,
then run the tool.
"""
import os
import re
import subprocess
from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ToolDesk</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#e9eef0;--ac:#0e8a8a;--ac2:#d3eceb;--hd:#26343a;--line:#c6d3d6;--code:#11191c;--codeink:#7ff0d6}</style></head><body><header><span class="logo">🧰</span><div><b>ToolDesk</b><small>Diagnostics runner · plugin path</small></div><nav><a href="/">Tools</a><a href="/plugins">Plugins</a></nav></header><main>"""
_TAIL = """</main><footer>ToolDesk · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
PLUGIN_DIR = "/tmp/plugins"
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


@app.route("/")
def index():
    return page(
        "<h1>Diagnostics</h1>"
        "<p>Run the dashboard diagnostics tool, or upload a plugin "
        "(a small script). The tool runner searches the plugin path "
        "BEFORE the stock tools.</p>"
        '<h2>Run a tool</h2>'
        '<form action="/run" method="post">'
        '<label>tool <input name="tool" value="sysdiag"></label> '
        "<button>▶ run</button></form>"
        '<h2>Install a plugin</h2>'
        '<form action="/plugins" method="post">'
        '<label>plugin name <input name="name" value="mytool"></label> '
        '<label>script '
        '<input name="script" size="52" value="#!/bin/sh\necho hi"></label> '
        "<button>upload</button></form>"
        '<p class="hint">Search order: <code>/tmp/plugins</code> → <code>$PATH</code></p>'
        '<p><a href="/plugins">🧩 plugin list</a></p>')


@app.route("/plugins", methods=["GET", "POST"])
def plugins():
    if request.method == "POST":
        name = request.form.get("name", "")
        script = request.form.get("script", "")
        if not SAFE_NAME.match(name):
            return page("<h1>Rejected</h1><div class='card'><p class='bad'>plugin name may only use letters, digits, . _ -</p></div>")
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        path = os.path.join(PLUGIN_DIR, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(script)
        os.chmod(path, 0o755)
        return page(f"<h1>Plugin installed</h1><div class='card'><p>plugin {name} installed.</p></div>"
                    "<a class='back' href='/'>← back</a>")
    try:
        names = sorted(os.listdir(PLUGIN_DIR))
    except OSError:
        names = []
    items = "".join(f"<li>{n}</li>" for n in names) or "<li>(none)</li>"
    return page(f"<h1>Plugins</h1><div class='card'><ul>{items}</ul></div>"
                "<a class='back' href='/'>← back</a>")


@app.route("/run", methods=["POST"])
def run():
    tool = request.form.get("tool", "")
    if not SAFE_NAME.match(tool):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>bad tool name</p></div>")
    try:
        out = subprocess.run(
            f"PATH={PLUGIN_DIR}:$PATH {tool}", shell=True,
            capture_output=True, text=True, timeout=10)
        body = (out.stdout + out.stderr).strip() or "(no output)"
    except Exception as e:
        body = f"error: {e}"
    return page(f"<h1>{tool}</h1><pre>{body}</pre><a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
