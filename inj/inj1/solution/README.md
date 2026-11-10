# inj1 (LibraryNet) — intended solution & staff notes

## Path
1. `POST /ping` with `host=localhost; cat /flag/flag` (any command splitter
   works: `;`, `&&`, backticks, `$(...)`).
2. The command output is reflected in the page; it carries the flag.

## Why it is what it is
- `subprocess.run(..., shell=True)` with an interpolated argument (CWE-78,
  the lecture's `ping` argument-exploitation example).
- The flag is NOT in the app: it is `/flag/flag` (live mount). `/app/config.env`
  carries a decoy `flag{...}` to punish "read the config" shortcuts.

## Grading discriminators
- Names the vector as OS command injection (shell metacharacter splitting),
  not "the app is vulnerable".
- Explains why the app itself contains no flag and where the flag actually
  lives; notes the decoy.
- Fix: run `ping` as an argument list without a shell (`shlex.split` +
  `shell=False`) and validate the host format (hostname/IP allowlist).
