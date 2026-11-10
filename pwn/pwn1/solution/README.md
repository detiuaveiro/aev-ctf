# pwn1 (formerly ret2win) — intended solution & staff notes

## Bug
`vuln()` reads into a 64-byte stack buffer with `gets()` — unbounded write.

## Primitive
Straight saved-return-address overwrite. No stack canary
(`-fno-stack-protector`), no PIE (`-no-pie`), so `win()` is at a fixed address.

## Path
1. Find the offset to the saved return address: `64` (buffer) + `8` (saved
   `rbp`) = **72** bytes. (Confirm with a cyclic pattern in GDB.)
2. Resolve `win()`: `objdump -d build/vuln | grep '<win>:'` or
   `ELF('build/vuln').symbols['win']`.
3. Payload: `b"A"*72 + p64(win)`.

See `solve.py` for the reference exploit. It must recover the flag with no
manual steps — CI runs it on every push.

## Grading discriminators (for the write-up / defense)
- Did they find the offset *by reasoning* (cyclic pattern, watching `$rip`), or
  guess? Ask them to derive 72 at the defense.
- Do they explain **why** `win()` is at a fixed address here and would not be in
  a PIE binary? This separates recall from understanding.
- Live perturbation for the defense: rebuild with a `dummy[16]` added to the
  frame, or enable the stack canary, and ask them to re-solve. The offset
  changes / the approach must change — a received exploit does not survive this.

## Hardened deployment (swap for the socat runtime)
Replace the runtime stage with `pwn.red/jail` (nsjail) for per-connection
isolation and resource limits. The jail clears the child environment, so inject
the flag via `/srv/app/flag.txt` (readable by the run user) instead of `-e FLAG`,
and have `win()` read the file rather than `getenv`.
