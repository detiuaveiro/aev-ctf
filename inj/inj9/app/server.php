<?php
// inj9 (PicLink) -- SSRF via an unvalidated URL scheme.
//
// The product-image "preview" fetches whatever URL the merchandiser pastes,
// with file_get_contents() -- which supports file:// as well as http(s)://.
// Nothing checks the scheme:
//
//     url = file:///flag/flag
//
// The fetched bytes are served straight back with Content-Type: image/png.
// The app itself never reads /flag/flag; the fetch does.

header('Content-Type: text/html; charset=utf-8');

const HEAD = <<<'EOT'
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PicLink</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#f2f4fb;--ac:#6a4cff;--ac2:#e8e4ff;--hd:linear-gradient(90deg,#6a4cff,#c04cff);--line:#d8dcf0}.thumb{height:150px;border:2px dashed var(--line);border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--mut);font-size:42px;background:repeating-conic-gradient(#fff 0 25%,#eef0fa 0 50%) 0 0/20px 20px}</style></head><body><header><span class="logo">🖼️</span><div><b>PicLink</b><small>Product image proxy · CDN link checker</small></div><nav><a href="/">Preview</a></nav></header><main>
EOT;
const TAIL = <<<'EOT'
</main><footer>PicLink · Aev lab environment · training use only</footer></body></html>
EOT;

function page(string $body): string {
    return HEAD . $body . TAIL;
}

function esc(string $s): string {
    return htmlspecialchars($s, ENT_QUOTES, 'UTF-8');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['url'])) {
    $url = $_POST['url'];
    $ctx = stream_context_create(['http' => ['timeout' => 5]]);
    $data = @file_get_contents($url, false, $ctx);
    if ($data === false) {
        http_response_code(502);
        echo page("<h1>Image Preview</h1><div class='card'><p class='bad'>fetch failed for <code>"
            . esc($url) . "</code></p></div><a class='back' href='/'>← back</a>");
    } else {
        // "It's an image, obviously."
        header('Content-Type: image/png');
        echo $data;
    }
} else {
    echo page("<h1>Product Image Proxy</h1>"
        . "<p>Preview a remote product image by URL (our CDN link checker).</p>"
        . "<form action='/preview' method='post'>"
        . "<label>image URL "
        . "<input name='url' size='56' value='https://cdn.aev.store/img/A1-042.png'></label> "
        . "<button>🔗 preview</button></form>"
        . "<h2>Preview</h2><div class='thumb'>🖼️</div>"
        . "<p class='hint'>The fetched image is returned as-is.</p>");
}
