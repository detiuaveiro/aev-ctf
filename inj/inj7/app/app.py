"""inj7 (DeskOne) -- OS command injection through the ticket log line.

Ticket requests are appended to the desk log through a shell:
    echo <line> >> /tmp/tickets.log      (shell=True, unquoted line)
The requester passes a "sanitizer" that strips ; | & -- but command
substitution survives:
    requester = x$(cat /flag/flag)
The flag does NOT appear in the /ticket response itself: it is written into
the log file and surfaces on the log-tail page. The app never reads
/flag/flag; the shell does, on the student's behalf.

Intended solution: inject $() into the requester, then read /log.
"""
import re
import subprocess
import time
from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DeskOne</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#eef3f9;--ac:#1b6ec2;--ac2:#dbeaf8;--hd:linear-gradient(90deg,#0f4c8a,#1b6ec2);--line:#cfdbe8;--code:#0d1b2a;--codeink:#b8d8ff}</style></head><body><header><span class="logo">🎫</span><div><b>DeskOne</b><small>IT service desk · ticket queue</small></div><nav><a href="/">New ticket</a><a href="/log">Desk log</a></nav></header><main>"""
_TAIL = """</main><footer>DeskOne · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
LOG = "/tmp/tickets.log"
BLOCKED = re.compile(r"[;|&]")


def sanitize(text: str) -> str:
    return BLOCKED.sub("", text)


@app.route("/")
def index():
    return page(
        "<h1>Service Tickets</h1>"
        "<p>Open a service ticket. Every request is written to the desk log.</p>"
        '<div class="grid">'
        '<div class="stat"><b>7</b><span>open tickets</span></div>'
        '<div class="stat"><b>2</b><span>high priority</span></div>'
        '<div class="stat"><b>~35 min</b><span>avg response</span></div></div>'
        '<form action="/ticket" method="post">'
        '<label>requester <input name="requester" value="jdoe"></label> '
        '<label>priority '
        '<select name="prio"><option>low</option><option>high</option></select>'
        "</label> "
        "<button>open ticket</button></form>"
        '<p><a href="/log">📜 desk log</a></p>')


@app.route("/ticket", methods=["POST"])
def ticket():
    requester = sanitize(request.form.get("requester", "")).strip() or "anon"
    prio = request.form.get("prio", "low")
    line = f"[{time.strftime('%H:%M:%S')}] TICKET requester={requester} prio={prio}"
    # Logging "the way the ops script always did it".
    try:
        subprocess.run(f"echo {line} >> {LOG}", shell=True,
                       capture_output=True, text=True, timeout=5)
    except Exception:
        pass
    return page(f"<h1>Ticket opened</h1>"
                f"<div class='card'><p>Ticket opened for {requester} (prio {prio}). "
                f"See the <a href='/log'>desk log</a>.</p></div>"
                "<a class='back' href='/'>← new ticket</a>")


@app.route("/log")
def log():
    try:
        with open(LOG, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()[-20:]
    except OSError:
        lines = []
    body = "<br>".join(lines) or "(empty)"
    return page(f"<h1>Desk log (last 20)</h1><pre>{body}</pre>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
