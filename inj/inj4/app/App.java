import com.sun.net.httpserver.HttpServer;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.StringReader;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * inj4 (Catalogo) -- catalogue record import (XML).
 *
 * The import parser is a plain DocumentBuilderFactory with no security
 * features set: DOCTYPE external entities (file://) are resolved
 * (CWE-611, XXE). The flag lives at /flag/flag and is reflected as the
 * text of the imported record.
 */
public class App {
    static final String HEAD = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Catalogo</title><style>:root{--bg:#f6f4ee;--panel:#fff;--ink:#222;--mut:#6b6b6b;--ac:#2f6f4f;--ac2:#e7f1ea;--hd:var(--ac);--line:#ddd;--code:#14201a;--codeink:#cfe9d8;--in:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--hd);color:#fff;padding:14px 28px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 8px #0003}header .logo{font-size:28px;line-height:1}header b{font-size:19px;letter-spacing:.4px;display:block}header small{opacity:.8;font-size:12px;display:block}header nav{margin-left:auto}header nav a{color:#fff;opacity:.85;margin-left:18px;text-decoration:none;font-size:14px}header nav a:hover{opacity:1;text-decoration:underline}main{max-width:880px;margin:26px auto;padding:0 18px}h1{font-size:22px;margin:0 0 8px}h2{font-size:15px;margin:24px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--mut)}p{margin:.3em 0 1em}form{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}label{display:flex;flex-direction:column;font-size:11px;font-weight:700;color:var(--mut);gap:4px;text-transform:uppercase;letter-spacing:.5px}input,select,textarea{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--in);color:var(--ink);min-width:190px;text-transform:none;letter-spacing:0;font-weight:400}input:focus,select:focus,textarea:focus{outline:2px solid var(--ac);outline-offset:0}textarea{width:100%}label:has(textarea){flex:1 1 100%}button{background:var(--ac);color:#fff;border:0;border-radius:6px;padding:9px 20px;font-weight:700;cursor:pointer;font-size:14px}button:hover{filter:brightness(1.12)}pre{background:var(--code);color:var(--codeink);padding:14px 16px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-all;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;border:1px solid #0003}code{background:var(--ac2);color:var(--ink);padding:1px 6px;border-radius:4px;font-size:13px}a{color:var(--ac)}a.back{display:inline-block;margin-top:6px;text-decoration:none;font-weight:600}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 16px;box-shadow:0 1px 3px #0001}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:0 0 16px}.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}.stat b{display:block;font-size:24px;color:var(--ac)}.stat span{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 16px}th,td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);font-size:14px}th{background:var(--ac2);font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--mut)}.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:700;background:var(--ac2);color:var(--ac)}.ok{color:#1b8a4b}.warn{color:#c47a00}.bad{color:#c0392b}ul{padding-left:20px}.hint{color:var(--mut);font-size:13px}footer{text-align:center;color:var(--mut);font-size:12px;padding:26px}:root{--bg:#efe6d2;--panel:#fbf6e9;--ac:#7a4a21;--ac2:#eadbb8;--hd:linear-gradient(90deg,#4e2f14,#7a4a21);--line:#cdb98a;--code:#2a1d10;--codeink:#f0dfb4}h1,h2{font-family:Georgia,serif}li{margin:3px 0}body{background-image:radial-gradient(#0000000d 1px,#0000 1px);background-size:14px 14px}</style></head><body><header><span class="logo">🗃️</span><div><b>Catalogo</b><small>Catalogue record import · Biblioteca Aev</small></div><nav><a href="/">Import</a></nav></header><main>""";
    static final String TAIL = """
</main><footer>Catalogo · Aev lab environment · training use only</footer></body></html>""";

    static String page(String body) {
        return HEAD + body + TAIL;
    }

    static final List<String> RECENT = new ArrayList<>();

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/", ex -> {
            byte[] body = indexPage();
            ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
            ex.sendResponseHeaders(200, body.length);
            ex.getResponseBody().write(body);
            ex.close();
        });
        server.createContext("/import", ex -> {
            String xml = xmlFromBody(new String(readAll(ex.getRequestBody()), StandardCharsets.UTF_8));
            String title = importRecord(xml);
            byte[] body = page("<h1>Record imported</h1>"
                    + "<p>Imported record:</p><pre>" + esc(title) + "</pre>"
                    + "<a class='back' href='/'>← back</a>").getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
            ex.sendResponseHeaders(200, body.length);
            ex.getResponseBody().write(body);
            ex.close();
        });
        server.start();
        System.out.println("Catalogo listening on :8080");
    }

    /**
     * The UI form posts application/x-www-form-urlencoded with an 'xml'
     * field, while the reference solve posts the raw XML as the body.
     * Accept both: a body that starts with '<' is the XML itself; anything
     * else is treated as a urlencoded form and the 'xml' field is decoded.
     * (Bug 2026-10-30: the raw body "xml=%3Crecord…" was parsed as XML and
     * the parser answered "Content is not allowed in the prolog".)
     */
    static String xmlFromBody(String body) {
        if (body.stripLeading().startsWith("<")) {
            return body;
        }
        for (String pair : body.split("&")) {
            int eq = pair.indexOf('=');
            String name = java.net.URLDecoder.decode(
                    eq < 0 ? pair : pair.substring(0, eq), StandardCharsets.UTF_8);
            if (name.trim().equals("xml")) {
                return java.net.URLDecoder.decode(
                        pair.substring(eq + 1), StandardCharsets.UTF_8);
            }
        }
        return body;
    }

    static String importRecord(String xml) {
        try {
            DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
            // NOTE: no disallow-doctype-decl, no external-entity lockdown:
            // the "it worked on my machine" default.
            Document doc = f.newDocumentBuilder()
                    .parse(new org.xml.sax.InputSource(new StringReader(xml)));
            String t = doc.getDocumentElement().getTextContent().trim();
            synchronized (RECENT) {
                RECENT.add(t);
                if (RECENT.size() > 5) {
                    RECENT.remove(0);
                }
            }
            return t.isEmpty() ? "(empty record)" : t;
        } catch (Exception e) {
            return "parse error: " + e.getMessage();
        }
    }

    static byte[] indexPage() {
        StringBuilder recent = new StringBuilder();
        synchronized (RECENT) {
            for (String t : RECENT) {
                recent.append("<li>").append(esc(t)).append("</li>");
            }
        }
        return page("<h1>Catalogue Import</h1>"
                + "<p>Import a catalogue record (XML). The record's text is shown below.</p>"
                + "<form action='/import' method='post'>"
                + "<label>record (XML)<textarea name='xml' rows='6' cols='64' placeholder='<record><id>12</id><title>...</title></record>'></textarea></label>"
                + "<button>📥 import</button></form>"
                + "<h2>Recent imports</h2><div class='card'><ul>"
                + (recent.length() == 0 ? "<li class='hint'>no records imported yet</li>" : recent)
                + "</ul></div>")
                .getBytes(StandardCharsets.UTF_8);
    }

    static byte[] readAll(InputStream in) throws java.io.IOException {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        byte[] chunk = new byte[8192];
        int n;
        while ((n = in.read(chunk)) > 0) {
            buf.write(chunk, 0, n);
        }
        return buf.toByteArray();
    }

    static String esc(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }
}
