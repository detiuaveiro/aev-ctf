<?php
// inj8 (StockEye) -- inventory audit with an (incomplete) input filter.
//
// The audit runs a fixed two-step shell command with the user's path:
//     ls -la {path} && cat {path}
// A "sanitizer" strips ; | & $ newline backtick > < from the path --
// but NOT the glob '*', which the SHELL expands (the lecture's
// parameter-expansion slide). So path = /flag/* becomes
//     ls -la /flag/* && cat /flag/*
// and the flag is cat'd. The app itself never reads /flag/flag.

header('Content-Type: text/html; charset=utf-8');

const HEAD = <<<'EOT'
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>StockEye</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#f3f1ec;--ac:#c77700;--ac2:#fbe8c4;--hd:#232323;--line:#d9d4c7;--code:#1c1a14;--codeink:#ffd27a}header{border-bottom:6px solid #c77700}</style></head><body><header><span class="logo">📦</span><div><b>StockEye</b><small>Warehouse inventory audit</small></div><nav><a href="/">Audit</a></nav></header><main>
EOT;
const TAIL = <<<'EOT'
</main><footer>StockEye · Aev lab environment · training use only</footer></body></html>
EOT;

function page(string $body): string {
    return HEAD . $body . TAIL;
}

function esc(string $s): string {
    return htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
}

function sanitize(string $p): string {
    // The "security" the developer added: a blacklist.
    // Note what it does NOT strip: the glob.
    return str_replace(
        [';', '|', '&', '$', "\n", "\r", '`', '>', '<', "/flag/flag"],
        '',
        $p
    );
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['path'])) {
    $path = sanitize($_POST['path']);
    exec("ls -la $path && cat $path", $out, $rc);
    $body = implode("\n", $out);
    $page = page("<h1>Inventory Audit</h1>"
        . "<p>Audit of <code>" . esc($path) . "</code> (exit $rc):</p>"
        . "<pre>" . esc($body !== '' ? $body : '(no output)') . "</pre>"
        . "<a class='back' href='/'>← back</a>");
} else {
    $page = page("<h1>Inventory Audit</h1>"
        . "<p>Audit any directory or file the service can see: it lists it, "
        . "then shows its contents.</p>"
        . "<div class='grid'>"
        . "<div class='stat'><b>4,212</b><span>SKUs tracked</span></div>"
        . "<div class='stat'><b>18</b><span>low-stock alerts</span></div>"
        . "<div class='stat'><b>3</b><span>warehouses</span></div></div>"
        . "<form action='/audit' method='post'>"
        . "<label>path <input name='path' value='/app/inventory.csv'></label> "
        . "<button>🔍 audit</button></form>");
}
echo $page;
