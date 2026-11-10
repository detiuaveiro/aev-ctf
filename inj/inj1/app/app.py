"""inj1 (LibraryNet) -- OS command injection in the node health check.

The 'ping the OPAC node' form interpolates the target into a shell pipeline:
    ping -c 1 <host>        (shell=True)
The app never touches the flag: the container user (ctf) can read /flag/flag
straight from the shell. A decoy FLAG sits in /app/config.env so that
'read the config' does not solve it (secrets-in-config is the mistake this
challenge punishes).

Intended solution: split the command (';' or backticks) and read /flag/flag.
"""
import subprocess
from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LibraryNet</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#f4efe3;--ac:#2d5a3d;--ac2:#e3eddd;--code:#0f1a13;--codeink:#9be3b0;--line:#d9d0bb;--hd:linear-gradient(90deg,#1f4130,#2d5a3d)}body{background-image:repeating-linear-gradient(90deg,#0000 0 38px,#0000000a 38px 40px)}</style></head><body><header><span class="logo">📚</span><div><b>LibraryNet</b><small>Systems Dashboard · Aev Public Library</small></div><nav><a href="/">Dashboard</a></nav></header><main>"""
_TAIL = """</main><footer>LibraryNet · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL


@app.route("/")
def index():
    return page(
        "<h1>Node health check</h1>"
        "<p>Quick health check of the catalogue nodes on the library LAN.</p>"
        '<div class="grid">'
        '<div class="stat"><b>3</b><span>OPAC nodes</span></div>'
        '<div class="stat"><b>12 ms</b><span>avg latency</span></div>'
        '<div class="stat"><b>99.9%</b><span>uptime (30d)</span></div></div>'
        '<form action="/ping" method="post">'
        '<label>OPAC node <input name="host" value="opac-1"></label> '
        "<button>ping</button></form>"
        "<h2>Known nodes</h2>"
        "<table><tr><th>node</th><th>role</th><th>status</th></tr>"
        '<tr><td>opac-1</td><td>public catalogue terminal</td><td><span class="pill">online</span></td></tr>'
        '<tr><td>opac-2</td><td>public catalogue terminal</td><td><span class="pill">online</span></td></tr>'
        '<tr><td>desk-1</td><td>circulation desk</td><td><span class="pill">online</span></td></tr></table>')


@app.route("/ping", methods=["POST"])
def ping():
    host = request.form.get("host", "")
    try:
        out = subprocess.run(
            f"ping -c 1 {host}", shell=True,
            capture_output=True, text=True, timeout=10)
        body = (out.stdout + out.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        body = "timeout"
    return page(f"<h1>ping {host}</h1><pre>{body}</pre>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
