"""snmp1 -- an SNMPv2c agent that leaks the flag through a private MIB.

The lab host runs this agent on UDP 161 with the default ``public`` community.
It is world-readable: anyone who sends a GET / GETNEXT / GETBULK gets an answer.

It exposes two things:

1. **Standard host information** -- the MIB-II system group (sysDescr,
   sysObjectID, sysUpTime, sysContact, sysName, sysLocation, sysServices) and a
   small interface table (ifNumber, ifIndex/ifDescr/ifSpeed/ifAdminStatus/
   ifOperStatus for ``lo`` and ``eth0``). Plausible, boring, realistic.

2. **A private enterprise tree** -- ``1.3.6.1.4.1.99999.1.1.*``. The first node
   (``...1.1.0``) is *the result of a script*: the agent runs ``/app/flag.sh``
   and returns its stdout. In the lab that script echoes ``$FLAG`` (the
   per-student derived flag, injected via the podman secret), so walking the
   tree hands the flag to anyone.

Intended solution: ``snmpwalk`` the host (community ``public``) and read the
flag out of the private tree. See ``solution/solve.py``.
"""
from __future__ import annotations

import bisect
import os
import signal
import socket
import subprocess
import sys
import threading
import time

import snmpcodec as c

START = time.time()

# The classic default communities. The "leak" is that the agent answers the
# world-readable ``public`` community; we also accept ``private``/``lab`` for
# realism. A request with any other community gets an error (notAccessible).
COMMUNITIES = {"public", "private", "lab"}

# The private OID that returns the status-script output (the flag).
FLAG_OID = "1.3.6.1.4.1.99999.1.1.0"
FLAG_SCRIPT = os.environ.get("FLAG_SCRIPT", "/app/flag.sh")
# Rolling flag (docs/plans/2026-10-09-rolling-flag-design.md): /flag is a
# read-only bind mount of the host's per-challenge flag directory. The agent
# serves the flag per request (the status script is re-run on every GET), so
# a rotation is visible without a restart. The env FLAG (podman secret) is
# the fallback for local/docker-compose runs where no mount exists.
FLAG_FILE = os.environ.get("FLAG_FILE", "/flag/flag")


def _fallback_flag() -> str:
    """The live flag from /flag/flag, else the env FLAG, else a placeholder."""
    try:
        with open(FLAG_FILE, encoding="utf-8") as fh:
            v = fh.read().strip()
        if v:
            return v
    except OSError:
        pass
    return os.environ.get("FLAG", "flag{snmp1_local_test}")

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "161"))


def flag_script_output() -> bytes:
    """Run the status script and return its stdout (the dynamic flag)."""
    try:
        r = subprocess.run(["/bin/sh", FLAG_SCRIPT], capture_output=True, timeout=5)
        out = (r.stdout or b"").strip()
        if out:
            return out
    except Exception:
        pass
    # Script missing/failing: fall back to the live flag file, then env.
    return _fallback_flag().encode()


def uptime_ticks() -> int:
    return int((time.time() - START) * 100)  # SNMP timeticks = centiseconds


def uptime_sec() -> int:
    return int(time.time() - START)


def build_tree():
    """The MIB as a list of ``(oid, kind, value)`` sorted by OID.

    ``kind`` in {"str", "int", "oid"}. The flag node's value is recomputed on
    every tree build (i.e. per request) so it is genuinely *the result of a
    script*, not a cached constant.
    """
    t = [
        # --- MIB-II system group (1.3.6.1.2.1.1) ---
        ("1.3.6.1.2.1.1.1.0", "str", "Linux lab-host 6.1.0-18 #1 SMP x86_64 GNU/Linux"),
        ("1.3.6.1.2.1.1.2.0", "oid", "1.3.6.1.4.1.8072.3.1"),
        ("1.3.6.1.2.1.1.3.0", "int", uptime_ticks()),
        ("1.3.6.1.2.1.1.4.0", "str", "NetOps <netops@lab.deti>"),
        ("1.3.6.1.2.1.1.5.0", "str", "lab-host"),
        ("1.3.6.1.2.1.1.6.0", "str", "Lab rack 2, shelf B"),
        ("1.3.6.1.2.1.1.7.0", "int", 72),
        # --- MIB-II interfaces (1.3.6.1.2.1.2) ---
        ("1.3.6.1.2.1.2.1.0", "int", 2),                 # ifNumber
        ("1.3.6.1.2.1.2.2.1.1.1", "int", 1),             # ifIndex.1
        ("1.3.6.1.2.1.2.2.1.2.1", "str", "lo"),          # ifDescr.1
        ("1.3.6.1.2.1.2.2.1.5.1", "int", 65536),         # ifSpeed.1
        ("1.3.6.1.2.1.2.2.1.7.1", "int", 1),             # ifAdminStatus.1 (up)
        ("1.3.6.1.2.1.2.2.1.8.1", "int", 1),             # ifOperStatus.1 (up)
        ("1.3.6.1.2.1.2.2.1.1.2", "int", 2),             # ifIndex.2
        ("1.3.6.1.2.1.2.2.1.2.2", "str", "eth0"),        # ifDescr.2
        ("1.3.6.1.2.1.2.2.1.5.2", "int", 1000000000),    # ifSpeed.2
        ("1.3.6.1.2.1.2.2.1.7.2", "int", 1),             # ifAdminStatus.2 (up)
        ("1.3.6.1.2.1.2.2.1.8.2", "int", 1),             # ifOperStatus.2 (up)
        # --- private enterprise tree (1.3.6.1.4.1.99999.1.1) -- the leak ---
        (FLAG_OID, "str", flag_script_output()),          # ...1.1.0  status script (flag)
        ("1.3.6.1.4.1.99999.1.1.1", "str", "2026.10.09"), # ...1.1.1  build
        ("1.3.6.1.4.1.99999.1.1.2", "int", uptime_sec()), # ...1.1.2  uptime (s)
        ("1.3.6.1.4.1.99999.1.1.3", "str", "lab-detl"),   # ...1.1.3  region token
    ]
    t.sort(key=lambda x: c.oid_key(x[0]))
    return t


def handle(data: bytes, sock: socket.socket, addr) -> None:
    try:
        msg = c.parse_message(data)
    except Exception:
        return  # not an SNMP message we understand; drop it

    comm = msg["community"] or b""
    reqid = msg["reqid"]
    version = msg.get("version", 1)  # 0 = SNMPv1, 1 = SNMPv2c
    community = comm if comm else b"public"

    # Unknown community -> notAccessible (error-status 2), no bindings.
    if comm and comm.decode("latin-1") not in COMMUNITIES:
        sock.sendto(c.build_response(reqid, [], community, error=2, eidx=0,
                                     version=version), addr)
        return

    tree = build_tree()
    keys = [c.oid_key(o) for o, _, _ in tree]
    ptag = msg["pdu_tag"]
    out = []

    for oid, _vtag, _vcontent in msg["bindings"]:
        if ptag == c.GET:
            i = bisect.bisect_left(keys, c.oid_key(oid))
            if i < len(tree) and tree[i][0] == oid:
                out.append(tree[i])
            else:
                out.append((oid, "null", None))  # noSuchObject
        elif ptag == c.GETNEXT:
            i = bisect.bisect_right(keys, c.oid_key(oid))
            if i < len(tree):
                out.append(tree[i])
            else:
                out.append((oid, "endofmib", None))
        elif ptag == c.GETBULK:
            rep = msg["maxrep"] if msg["maxrep"] > 0 else 1
            i = bisect.bisect_left(keys, c.oid_key(oid))
            for _ in range(rep):
                if i < len(tree):
                    out.append(tree[i])
                    i += 1
                else:
                    out.append((oid, "endofmib", None))
        else:
            # SET / anything else: echo back as noSuchObject (we are read-only).
            out.append((oid, "null", None))

    try:
        sock.sendto(c.build_response(reqid, out, community, version=version), addr)
    except OSError:
        pass


def main() -> int:
    def _shutdown(signum, frame):
        raise SystemExit(0)

    # This agent runs as PID 1 of the container's pid namespace, where the
    # kernel drops signals whose default action is to terminate -- without a
    # handler SIGTERM is ignored and `podman stop` hangs for its full timeout
    # before SIGKILL (exit 137). 2026-10-23 (docs/CHANGELOG.md §35.9).
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except OSError:
        pass
    s.bind((HOST, PORT))
    print(f"snmp1 agent listening on {HOST}:{PORT}/udp (community: public)",
          flush=True)
    try:
        while True:
            data, addr = s.recvfrom(65536)
            threading.Thread(target=handle, args=(data, s, addr),
                             daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        s.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
