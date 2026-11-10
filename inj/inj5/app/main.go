// inj5 (NightPack) -- OS command injection via the backup directory argument.
//
// The nightly backup one-liner interpolates the target directory into a
// shell string (the lecture's `tar` argument-exploitation example):
//
//	sh -c "tar czf /tmp/backup.tgz <dir> 2>&1"
//
// The app never touches the flag; the injected second command can read
// /flag/flag (live mount).
package main

import (
	"fmt"
	"net/http"
	"os/exec"
	"strings"
)

const head = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NightPack</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#0b1026;--panel:#121a3a;--ink:#dfe6ff;--mut:#8b97c7;--ac:#7c6cff;--ac2:#1f2850;--hd:linear-gradient(90deg,#0b1026,#231a5c);--line:#262f63;--code:#060919;--codeink:#a7f3d0;--in:#0b1026}body{background-image:radial-gradient(#ffffff22 1px,#0000 1px),radial-gradient(#ffffff14 1px,#0000 1px);background-size:90px 90px,47px 47px;background-position:0 0,20px 30px}</style></head><body><header><span class="logo">🌙</span><div><b>NightPack</b><small>Nightly backup runner</small></div><nav><a href="/">Backup</a></nav></header><main>`
const tail = `</main><footer>NightPack · Aev lab environment · training use only</footer></body></html>`

func page(body string) string {
	return head + body + tail
}

func main() {
	http.HandleFunc("/", index)
	http.HandleFunc("/backup", backup)
	fmt.Println("NightPack listening on :8080")
	http.ListenAndServe(":8080", nil)
}

func index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, page(`<h1>Nightly Backup</h1>
<p>Pack a store directory into tonight's backup archive.</p>
<div class="grid">
<div class="stat"><b>02:00</b><span>next scheduled run</span></div>
<div class="stat"><b>/tmp/backup.tgz</b><span>archive target</span></div>
<div class="stat"><b class="ok">ok</b><span>last run</span></div></div>
<form action="/backup" method="post">
<label>directory <input name="dir" value="catalog"></label>
<button>🌙 run backup</button>
</form>`))
}

func backup(w http.ResponseWriter, r *http.Request) {
	dir := r.FormValue("dir")
	// The backup one-liner the ops script has always used.
	out, err := exec.Command("sh", "-c",
		fmt.Sprintf("tar czf /tmp/backup.tgz %s 2>&1", dir)).CombinedOutput()
	body := string(out)
	if err != nil {
		body += "\n(error: " + err.Error() + ")"
	}
	if strings.TrimSpace(body) == "" {
		body = "(no output)"
	}
	fmt.Fprint(w, page("<h1>backup of "+esc(dir)+"</h1><pre>"+esc(body)+
		"</pre><a class='back' href='/'>← back</a>"))
}

func esc(s string) string {
	return strings.NewReplacer("&", "&amp;", "<", "&lt;", ">", "&gt;").Replace(s)
}
