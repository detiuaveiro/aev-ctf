"""inj12 (SessionVault) -- deserialization to RCE (Python pickle).

The support tool restores "workspaces": the client posts a base64 pickle,
the server unpickles it and previews the result. pickle.loads is code
execution by construction: an object's __reduce__ tells the unpickler to
call callable(*args) while reconstructing it. The server calls that code
with the service's own privileges.

The preview helper is the reflection point:

    def preview(obj):
        if hasattr(obj, "read"):        # "it may be a file-like workspace"
            return obj.read()
        if isinstance(obj, dict):
            return obj.get("name", "(unnamed)")
        return str(obj)

So a payload whose __reduce__ is (open, ('/flag/flag',)) unpickles into an
open file, and the preview reads it. The app never reads /flag/flag itself;
the unpickled object does, at load time.

Intended solution:
    class R:
        def __reduce__(self):
            return (open, ('/flag/flag',))
    blob = base64(pickle.dumps(R()))
"""
import base64
import binascii
import pickle

from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SessionVault</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#f1eefa;--ac:#5b3fc4;--ac2:#e5defa;--hd:linear-gradient(90deg,#2e1f6b,#5b3fc4);--line:#d5cbf0;--code:#1b1433;--codeink:#e0d6ff}</style></head><body><header><span class="logo">🔐</span><div><b>SessionVault</b><small>Workspace backup &amp; restore</small></div><nav><a href="/">Restore</a></nav></header><main>"""
_TAIL = """</main><footer>SessionVault · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL


def preview(obj):
    # The "friendly" preview: workspaces are usually dicts with a name,
    # but older exports were file-like. Handle both.
    if hasattr(obj, "read"):
        return obj.read()
    if isinstance(obj, dict):
        return obj.get("name", "(unnamed)")
    return str(obj)


@app.route("/")
def index():
    return page(
        "<h1>Workspace Restore</h1>"
        "<p>Lost your session? Paste the workspace blob from your "
        "backup (base64-encoded). We will show you what it contains.</p>"
        '<form action="/restore" method="post">'
        '<label>blob <input name="blob" size="64"></label> '
        "<button>🔓 restore</button></form>"
        '<div class="grid">'
        '<div class="stat"><b>AES-256</b><span>vault at rest</span></div>'
        '<div class="stat"><b>base64</b><span>export format</span></div>'
        '<div class="stat"><b class="ok">locked</b><span>vault status</span></div></div>')


@app.route("/restore", methods=["POST"])
def restore():
    blob = request.form.get("blob", "")
    try:
        raw = base64.b64decode(blob, validate=True)
    except (binascii.Error, ValueError):
        return page("<h1>Restore failed</h1><div class='card'><p class='bad'>not base64</p></div>"
                    "<a class='back' href='/'>← back</a>"), 400
    try:
        ws = pickle.loads(raw)
        name = preview(ws)
    except Exception as e:
        return page(f"<h1>Restore failed</h1><div class='card'><p class='bad'>restore failed: {type(e).__name__}: {e}</p></div>"
                    "<a class='back' href='/'>← back</a>"), 400
    return page(f"<h1>restored workspace</h1><pre>{name}</pre>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
