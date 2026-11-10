"""Minimal BER/DER codec + SNMPv2c PDU helpers (no external dependencies).

Shared by the agent (``app.py``) and the reference solve (``solution/solve.py``)
so there is one source of truth for the wire format. Covers GET / GETNEXT /
GETBULK requests and RESPONSE PDUs -- exactly what a snmpwalk-style
enumeration needs. This is *not* a general ASN.1 library; it encodes/decodes
the small set of SNMP value types this challenge uses (INTEGER, OCTET STRING,
OBJECT IDENTIFIER, NULL, noSuchObject, endOfMibView).

SNMPv2c message layout (BER/DER):

    SEQUENCE {
        version      INTEGER            -- 1 (v2c)
        community    OCTET STRING       -- e.g. b"public"
        PDU          <tagged SEQUENCE>  -- 0xA0 GET, 0xA1 GETNEXT, 0xA5 GETBULK,
                                         -- 0xA3 RESPONSE
    }

Request PDUs carry (request-id, error-status, error-index, variable-bindings);
GETBULK carries (request-id, non-repeaters, max-repetitions, variable-bindings).
A variable binding is ``SEQUENCE { OID, value }``.
"""
from __future__ import annotations

# ---- PDU tags ------------------------------------------------------------
GET = 0xA0
GETNEXT = 0xA1
SET = 0xA2
RESPONSE = 0xA3
GETBULK = 0xA5

# ---- value tags ----------------------------------------------------------
V_INT = 0x02
V_STR = 0x04
V_NULL = 0x05
V_OID = 0x06
V_NOSUCH = 0x80     # noSuchObject
V_ENDOFMIB = 0x81   # endOfMibView


# ---- low-level BER/DER ---------------------------------------------------

def _enc_len(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(b)]) + b


def tlv(tag: int, content: bytes) -> bytes:
    return bytes([tag & 0xFF]) + _enc_len(len(content)) + content


def enc_int(v: int) -> bytes:
    """Two's-complement INTEGER, minimal length (sign-extended)."""
    if v == 0:
        return b"\x02\x01\x00"
    nbytes = (v.bit_length() + 8) // 8
    return b"\x02" + _enc_len(nbytes) + v.to_bytes(nbytes, "big", signed=True)


def dec_int(content: bytes) -> int:
    return int.from_bytes(content, "big", signed=True)


def enc_str(s) -> bytes:
    if isinstance(s, str):
        s = s.encode("utf-8")
    return b"\x04" + _enc_len(len(s)) + s


def _enc_base128(v: int) -> bytes:
    if v == 0:
        return b"\x00"
    groups = []
    while v:
        groups.append(v & 0x7F)
        v >>= 7
    groups.reverse()
    out = bytearray()
    for i, g in enumerate(groups):
        out.append(g | 0x80 if i != len(groups) - 1 else g)
    return bytes(out)


def enc_oid(oid: str) -> bytes:
    parts = [int(x) for x in oid.split(".")]
    content = bytes([40 * parts[0] + parts[1]])
    for p in parts[2:]:
        content += _enc_base128(p)
    return b"\x06" + _enc_len(len(content)) + content


def dec_oid(content: bytes) -> str:
    first = content[0]
    parts = [first // 40, first % 40]
    i, cur = 1, 0
    while i < len(content):
        b = content[i]
        i += 1
        cur = (cur << 7) | (b & 0x7F)
        if not (b & 0x80):
            parts.append(cur)
            cur = 0
    return ".".join(str(p) for p in parts)


def oid_key(oid: str):
    """Ordering key for GETNEXT / GETBULK: the OID as a tuple of ints."""
    return tuple(int(x) for x in oid.split("."))


# ---- a tiny pull reader --------------------------------------------------

class _Reader:
    __slots__ = ("data", "pos")

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def tlv(self):
        tag = self.data[self.pos]
        self.pos += 1
        b = self.data[self.pos]
        self.pos += 1
        if b < 0x80:
            n = b
        else:
            k = b & 0x7F
            n = int.from_bytes(self.data[self.pos:self.pos + k], "big")
            self.pos += k
        content = self.data[self.pos:self.pos + n]
        self.pos += n
        return tag, content

    def done(self) -> bool:
        return self.pos >= len(self.data)


# ---- value encode / decode ----------------------------------------------

def enc_value(kind: str, value) -> bytes:
    if kind == "str":
        return enc_str(value)
    if kind == "int":
        return enc_int(value)
    if kind == "oid":
        return enc_oid(value)
    if kind == "null":
        return b"\x05\x00"
    if kind == "endofmib":
        return b"\x81\x00"
    if kind == "nosuch":
        return b"\x80\x00"
    raise ValueError(f"bad value kind {kind!r}")


def dec_value(tag: int, content: bytes):
    """Return ``(kind, value)``; kind in str/int/oid/null/nosuch/endofmib/raw."""
    if tag == V_STR:
        try:
            return "str", content.decode("utf-8")
        except UnicodeDecodeError:
            return "str", content.decode("latin-1")
    if tag == V_INT:
        return "int", dec_int(content)
    if tag == V_OID:
        return "oid", dec_oid(content)
    if tag == V_NULL:
        return "null", None
    if tag == V_NOSUCH:
        return "nosuch", None
    if tag == V_ENDOFMIB:
        return "endofmib", None
    return "raw", content


# ---- message builders (client side) -------------------------------------

def _bindings(oids) -> bytes:
    out = b""
    for o in oids:
        out += tlv(0x30, enc_oid(o) + b"\x05\x00")  # (oid, NULL)
    return tlv(0x30, out)


def build_get(reqid: int, oids, community: bytes = b"public") -> bytes:
    pdu = enc_int(reqid) + enc_int(0) + enc_int(0) + _bindings(oids)
    return tlv(0x30, enc_int(1) + enc_str(community) + tlv(GET, pdu))


def build_getnext(reqid: int, oids, community: bytes = b"public") -> bytes:
    pdu = enc_int(reqid) + enc_int(0) + enc_int(0) + _bindings(oids)
    return tlv(0x30, enc_int(1) + enc_str(community) + tlv(GETNEXT, pdu))


def build_getbulk(reqid: int, nonrep: int, maxrep: int, oids,
                  community: bytes = b"public") -> bytes:
    pdu = enc_int(reqid) + enc_int(nonrep) + enc_int(maxrep) + _bindings(oids)
    return tlv(0x30, enc_int(1) + enc_str(community) + tlv(GETBULK, pdu))


def build_response(reqid: int, bindings, community: bytes = b"public",
                   error: int = 0, eidx: int = 0, version: int = 1) -> bytes:
    """``bindings``: list of ``(oid_str, kind, value)``.

    ``version=1`` emits an SNMPv2c message (version INTEGER first);
    ``version=0`` emits SNMPv1 (community first, no version field).
    """
    vb = b""
    for oid, kind, value in bindings:
        vb += tlv(0x30, enc_oid(oid) + enc_value(kind, value))
    pdu = enc_int(reqid) + enc_int(error) + enc_int(eidx) + tlv(0x30, vb)
    head = enc_str(community) if version == 0 else enc_int(1) + enc_str(community)
    return tlv(0x30, head + tlv(RESPONSE, pdu))


# ---- message parser (server + client) -----------------------------------

def parse_message(data: bytes) -> dict:
    """Parse a full SNMPv1 or SNMPv2c message.

    v2c: SEQUENCE { version INTEGER, community, PDU }; v1: SEQUENCE
    { community, PDU } (no version field). A request with the v1 layout is
    common -- net-snmp defaults to v1 when no ``-v`` flag is given.

    Returns a dict with keys: version (0 = v1, 1 = v2c), community (bytes),
    pdu_tag, reqid, errstatus, eidx, bindings (list of
    ``(oid_str, value_tag, value_content_bytes)``), and -- for GETBULK --
    nonrep / maxrep.
    """
    r = _Reader(data)
    tag, content = r.tlv()  # top SEQUENCE
    if tag != 0x30:
        raise ValueError(f"not a SEQUENCE: 0x{tag:02x}")
    rr = _Reader(content)
    ftag, fcontent = rr.tlv()
    if ftag == 0x02:  # v2c layout: version INTEGER first
        version = dec_int(fcontent)
        _, comm = rr.tlv()
    elif ftag == 0x04:  # v1 layout: community OCTET STRING first
        version = 0
        comm = fcontent
    else:
        raise ValueError(f"neither version INTEGER nor community: 0x{ftag:02x}")
    ptag, pcontent = rr.tlv()
    pr = _Reader(pcontent)
    _, reqid = pr.tlv()
    msg = {
        "version": version,
        "community": comm,
        "pdu_tag": ptag,
        "reqid": dec_int(reqid),
        "errstatus": 0,
        "eidx": 0,
        "bindings": [],
        "nonrep": 0,
        "maxrep": 0,
    }
    if ptag == GETBULK:
        _, nr = pr.tlv()
        _, mr = pr.tlv()
        msg["nonrep"] = dec_int(nr)
        msg["maxrep"] = dec_int(mr)
    else:
        _, es = pr.tlv()   # error-status
        _, ei = pr.tlv()   # error-index
        msg["errstatus"] = dec_int(es)
        msg["eidx"] = dec_int(ei)
    if ptag in (GET, GETNEXT, SET, RESPONSE, GETBULK):
        _, vbs = pr.tlv()
        vr = _Reader(vbs)
        while not vr.done():
            _, b = vr.tlv()
            br = _Reader(b)
            _, oid = br.tlv()              # oid = OID content bytes
            val_tag, val_content = br.tlv()  # value = (tag, content)
            msg["bindings"].append((dec_oid(oid), val_tag, val_content))
    return msg
