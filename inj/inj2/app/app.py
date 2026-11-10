"""inj2 (ShelfTag) -- OS command injection via a newline the filter misses.

The label service builds a shell one-liner from the label text:
    printf '%s\\n' <text> > /tmp/label_<sku>.txt && cat /tmp/label_<sku>.txt
A "sanitizer" strips ; | & $ and backticks from the text -- but not
newlines. An unquoted newline terminates the first command, so the second
line runs on its own (and owns the redirection). The flag is /flag/flag.

Intended solution: label text = "x<NEWLINE>cat /flag/flag".
"""
import re
import subprocess
from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ShelfTag</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#fff7e0;--ac:#e07b00;--ac2:#ffe9c2;--hd:#2b2b2b;--line:#ecd9a8;--code:#fffdf5;--codeink:#222}header{border-bottom:4px solid #e07b00}pre{font-size:18px;letter-spacing:1px;border:2px dashed #222;background:#fffdf5;color:#222;text-align:center;border-radius:6px;box-shadow:3px 3px 0 #e07b00}</style></head><body><header><span class="logo">🏷️</span><div><b>ShelfTag</b><small>Label Service · back-room printer</small></div><nav><a href="/">Print label</a></nav></header><main>"""
_TAIL = """</main><footer>ShelfTag · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL

# The "security" the developer added: a blacklist.
# Note what it does NOT strip: the newline.
BLOCKED = re.compile(r"[;|&$\`]")


def sanitize(text: str) -> str:
    return BLOCKED.sub("", text)


@app.route("/")
def index():
    return page(
        "<h1>Label Service</h1>"
        "<p>Queue a shelf label for the back-room printer.</p>"
        '<form action="/label" method="post">'
        '<label>SKU <input name="sku" value="A1-042"></label> '
        '<label>text <input name="text" value="Fiction / Row 4"></label> '
        "<button>🖨️ print</button></form>"
        '<div class="grid">'
        '<div class="stat"><b>0</b><span>jobs queued</span></div>'
        '<div class="stat"><b>62 mm</b><span>label width</span></div>'
        '<div class="stat"><b class="ok">ready</b><span>printer status</span></div></div>')


@app.route("/label", methods=["POST"])
def label():
    sku = re.sub(r"[^A-Za-z0-9_-]", "", request.form.get("sku", "L1")) or "L1"
    text = sanitize(request.form.get("text", ""))
    path = f"/tmp/label_{sku}.txt"
    try:
        out = subprocess.run(
            f"printf '%s\\n' {text} > {path} && cat {path}",
            shell=True, capture_output=True, text=True, timeout=10)
        body = (out.stdout + out.stderr).strip() or "(blank label)"
    except Exception as e:
        body = f"error: {e}"
    return page(f"<h1>label {sku}</h1><p class='hint'>Printed to the back-room printer:</p>"
                f"<pre>{body}</pre>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
