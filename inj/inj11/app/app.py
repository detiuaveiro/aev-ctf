"""inj11 (LogWarden) -- second-order OS command injection.

Two code paths, one tainted value:

  1. POST /config  stores the shipper's log directory. The validation is a
     "looks like a path" check (must start with /) -- tuned for the STORE
     context, where a string is just data.
  2. POST /ship    the nightly shipper reads the stored value and builds a
     shell command from it:
         sh -c "ls -la <logdir> && tail -n 5 <logdir>/app.log"
     In the EXECUTE context the same string is code.

The value is stored first (harmless, "just a path") and executed later by
code the developer never connected to the input. The app never reads
/flag/flag; the injected shell does, at ship time.

Intended solution:
    logdir = "/tmp/logs; cat /flag/flag"
    POST /config  (stored, validated, echoed back)
    POST /ship    (flag appears in the shipper output)
"""
import json
import os
import subprocess

from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LogWarden</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#14171c;--panel:#1c2027;--ink:#e3e6eb;--mut:#8a93a2;--ac:#e0a526;--ac2:#2c2a1b;--hd:#0c0e11;--line:#2d333d;--code:#08090b;--codeink:#7ee787;--in:#14171c}button{color:#14171c}header{border-bottom:2px solid #e0a526}</style></head><body><header><span class="logo">🛡️</span><div><b>LogWarden</b><small>Log shipper · tail, ship, sink</small></div><nav><a href="/">Shipper</a></nav></header><main>"""
_TAIL = """</main><footer>LogWarden · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
CONFIG = "/tmp/config.json"
DEFAULT_DIR = "/tmp/logs"


def seed():
    os.makedirs(DEFAULT_DIR, exist_ok=True)
    log = os.path.join(DEFAULT_DIR, "app.log")
    if not os.path.exists(log):
        with open(log, "w") as fh:
            fh.write("2026-10-23T09:00:00Z INFO  logwarden shipper started\n"
                     "2026-10-23T09:00:01Z INFO  142 lines shipped to sink\n")
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w") as fh:
            json.dump({"logdir": DEFAULT_DIR}, fh)


def load_config():
    try:
        with open(CONFIG) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"logdir": DEFAULT_DIR}


@app.route("/")
def index():
    cfg = load_config()
    return page(
        "<h1>Log Shipper</h1>"
        "<p>The shipper tails the configured log directory and pushes it "
        "to the sink. Change the directory, then let the shipper run.</p>"
        f'<div class="card"><span class="hint">CURRENT LOGDIR</span><br>'
        f'<code>{cfg.get("logdir", DEFAULT_DIR)}</code> '
        '<span class="pill">sink: ok</span></div>'
        '<h2>1 · Configure</h2>'
        '<form action="/config" method="post">'
        '<label>logdir <input name="logdir" size="40" value="'
        + cfg.get("logdir", DEFAULT_DIR) + '"></label> '
        "<button>save</button></form>"
        '<h2>2 · Ship</h2>'
        '<form action="/ship" method="post"><button>▶ run shipper now</button></form>')


@app.route("/config", methods=["POST"])
def config():
    logdir = request.form.get("logdir", "").strip()
    # The "security": it must be an absolute path. That is all the store
    # context needs to know. (It says nothing about the execute context.)
    if not logdir.startswith("/"):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>logdir must be an absolute path</p></div>"), 400
    with open(CONFIG, "w") as fh:
        json.dump({"logdir": logdir}, fh)
    return page(f"<h1>Config saved</h1><div class='card'><p>config saved: <code>{logdir}</code>. "
                "The shipper will pick it up on its next run.</p></div>"
                "<a class='back' href='/'>← back</a>")


@app.route("/ship", methods=["POST"])
def ship():
    logdir = load_config().get("logdir", DEFAULT_DIR)
    try:
        out = subprocess.run(
            f"ls -la {logdir} && tail -n 5 {logdir}/app.log",
            shell=True, capture_output=True, text=True, timeout=10)
        body = (out.stdout + out.stderr).strip() or "(no output)"
    except Exception as e:
        body = f"error: {e}"
    return page(f"<h1>shipper run (logdir <code>{logdir}</code>)</h1>"
                f"<pre>{body}</pre><a class='back' href='/'>← back</a>")


seed()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
