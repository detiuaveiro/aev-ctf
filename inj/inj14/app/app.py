"""inj14 (GateKeeper) -- WAF evasion: double-encoding + HTTP parameter
pollution, and why allowlisting beats metacharacter blocking.

The admin API runs a diagnostic command:

    /run?cmd=<command>        ->  sh -c <command>

In front of it sits a "WAF" with three realistic, documented flaws:

  1. It blocks metacharacters (; | & $ ` and CR/LF) -- a blacklist, not an
     allowlist.
  2. It inspects the cmd value after exactly ONE percent-decode (the
     framework's). The app, "defensively", percent-decodes its value a
     second time. So %253b reaches the WAF as %3b (clean) and the app as ;
     (live). Double-encoding bypass.
  3. It inspects the FIRST occurrence of cmd. The app routes on the LAST
     occurrence. So ?cmd=ls&cmd=<payload> passes the WAF and the app runs
     the second value. HTTP parameter pollution.

The admin API itself only runs a small allowlisted set of diagnostic
commands (ls/ps/df/du/uptime/whoami/id/free/date/stat/pwd/hostname) -- the
enforcement is on the final, twice-decoded string the app is about to run,
checking only its FIRST token, so a chained second command (after ; or a
subshell) is not inspected. A bare `cat /flag/flag` never reaches the
allowlist's position-zero reader: `cat` is not an allowed diagnostic, full
stop. Both doors instead lead with an allowed command (`ls`) and chain the
real read behind it.

Both doors are independent; either solves it. The app never reads
/flag/flag; the injected shell does.

Intended solutions (note the leading "ls": a bare "; ..." is a shell
syntax error -- the separator needs a command in front of it):
    door 1 (double encoding):  /run?cmd=ls%253b+cat+/flag/flag
        (wire: %253b -> WAF sees %3b -> app decodes to ;)
    door 2 (HPP):              /run?cmd=ls&cmd=ls%3b+cat+/flag/flag
        (WAF inspects "ls"; app takes the last value)
"""
import re
import subprocess
import urllib.parse

from flask import Flask, request

app = Flask(__name__)


_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GateKeeper</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#1b1b1f;--panel:#25262c;--ink:#ececf0;--mut:#9a9ba8;--ac:#e5484d;--ac2:#3a2022;--hd:#0f0f12;--line:#34353d;--code:#0b0b0e;--codeink:#ffb4b4;--in:#1b1b1f}header{border-bottom:3px solid #e5484d}</style></head><body><header><span class="logo">🚧</span><div><b>GateKeeper</b><small>Admin diagnostics behind the WAF</small></div><nav><a href="/">Diagnostics</a></nav></header><main>"""
_TAIL = """</main><footer>GateKeeper · Aev lab environment · training use only</footer></body></html>"""


def page(body):
    return _HEAD + body + _TAIL
META = re.compile(r"[;|&$\`]")
ALLOWED_CMDS = {"ls", "ps", "df", "du", "uptime", "whoami", "id", "free",
                "date", "stat", "pwd", "hostname"}


_FIRST_CMD = re.compile(r"^\s*([A-Za-z0-9_./-]+)")


def _allowed(v: str) -> bool:
    """App-level diagnostic allowlist, checked on the first token of the
    final (twice-decoded) string only -- a chained command after the
    allowed one is not re-checked, which is the intended hole. The token is
    matched on command-name characters only, so "ls;" (no space before the
    separator) still reads as "ls", not as one opaque word."""
    m = _FIRST_CMD.match(v)
    return bool(m) and m.group(1) in ALLOWED_CMDS


def _bad(s: str) -> bool:
    return bool(META.search(s)) or "\n" in s or "\r" in s


def _blocked():
    return page("<h1>403</h1><div class='card'><p class='bad'>🚫 WAF: request blocked</p>"
                "<p class='hint'>Rule: metacharacter filter. Incident logged.</p></div>"
                "<a class='back' href='/'>← back</a>"), 403


@app.before_request
def waf():
    # The WAF. It inspects the cmd parameter it routes on -- the FIRST
    # occurrence, as the framework handed it (one percent-decode from the
    # wire) -- plus the raw request body. It blocks metacharacters.
    v = request.args.get("cmd")
    if v is not None and _bad(v):
        return _blocked()
    body = request.get_data(as_text=True)
    if body and _bad(body):
        return _blocked()
    return None


@app.route("/")
def index():
    return page(
        "<h1>Admin Diagnostics</h1>"
        "<p>Run a diagnostic command on the service. A WAF inspects "
        "each command before the app sees it.</p>"
        '<form action="/run" method="get">'
        '<label>cmd <input name="cmd" size="48" value="ls -la /app"></label> '
        "<button>run</button></form>"
        '<div class="grid">'
        '<div class="stat"><b class="ok">ON</b><span>WAF status</span></div>'
        '<div class="stat"><b>blacklist</b><span>rule mode</span></div>'
        '<div class="stat"><b>0</b><span>blocked (session)</span></div></div>')


@app.route("/run", methods=["GET", "POST"])
def run():
    vals = request.args.getlist("cmd")
    if not vals:
        vals = request.form.getlist("cmd")
    if not vals:
        return index()
    # The app routes on the LAST occurrence of the parameter...
    v = vals[-1]
    # ...and percent-decodes its value again, "in case the client
    # double-encoded" (the second decode the WAF never applies).
    v = urllib.parse.unquote(v)
    if not _allowed(v):
        return page("<h1>Rejected</h1><div class='card'><p class='bad'>not a recognised diagnostic command"
                    "</p></div><a class='back' href='/'>← back</a>"), 400
    try:
        out = subprocess.run(v, shell=True,
                             capture_output=True, text=True, timeout=10)
        body = (out.stdout + out.stderr).strip() or "(no output)"
    except Exception as e:
        body = f"error: {e}"
    return page(f"<h1>run <code>{v}</code></h1><pre>{body}</pre>"
                "<a class='back' href='/'>← back</a>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
