/* inj6 (CardCraft) -- SSTI in the user-supplied gift-card design (EJS).

The store lets gift-givers bring their own card "design": a small HTML
template with <%= recipient %> / <%= message %> slots, filled
server-side with ejs.render. Nothing stops the design ITSELF from being
EJS code. (EJS 3 gives the template the JS globals, so builtins are
reachable without a direct `require` in scope:)

    <%= process.getBuiltinModule('child_process').execSync('cat /flag/flag').toString() %>

Flag: /flag/flag, live. The app itself never reads the flag.
*/
const express = require("express");
const ejs = require("ejs");

const HEAD = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CardCraft</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#fff0f5;--ac:#d6336c;--ac2:#ffe0ec;--hd:linear-gradient(90deg,#d6336c,#f08c00);--line:#f3c4d6;--code:#fffdf8;--codeink:#4a2a38}pre{background:#fffdf8;border:3px double #d6a24a;font-family:Georgia,serif;font-size:18px;text-align:center;padding:28px;border-radius:14px;box-shadow:0 6px 18px #d6336c33}</style></head><body><header><span class="logo">🎁</span><div><b>CardCraft</b><small>Gift cards, your design</small></div><nav><a href="/">Design a card</a></nav></header><main>`;
const TAIL = `</main><footer>CardCraft · Aev lab environment · training use only</footer></body></html>`;
const page = (body) => HEAD + body + TAIL;

const app = express();
app.use(express.urlencoded({ extended: false }));

app.get("/", (req, res) => {
  res.send(page(`
    <h1>Design a gift card</h1>
    <p>Write the message, and optionally bring your own card design:
    a small HTML template with <code>&lt;%= recipient %&gt;</code> and
    <code>&lt;%= message %&gt;</code> slots.</p>
    <form action="/card" method="post">
      <label>recipient <input name="recipient" value="M. Silva"></label>
      <label>message <input name="message" value="Happy birthday!"></label>
      <label>design
      <textarea name="design" rows="5" cols="64">&lt;div class="card"&gt;To: &lt;%= recipient %&gt;&lt;br&gt;&lt;%= message %&gt;&lt;/div&gt;</textarea></label><br>
      <button>🎁 print card</button>
    </form>
    <p class="hint">Tip: slots are filled server-side when the card is printed.</p>`));
});

app.post("/card", (req, res) => {
  const { recipient, message, design } = req.body;
  let card;
  try {
    card = ejs.render(design, { recipient, message });
  } catch (e) {
    res.status(500).send(page(`<h1>Print failed</h1><pre>template error: ${e.message}</pre><a class='back' href='/'>← back</a>`));
    return;
  }
  res.send(page(`<h1>Card preview</h1><pre>${card}</pre><a class='back' href='/'>← back</a>`));
});

app.listen(8080, () => console.log("CardCraft listening on :8080"));
