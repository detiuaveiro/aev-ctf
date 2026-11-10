# inj8 (StockEye) — intended solution & staff notes

## Path
1. Probe: `POST /audit` with `path=/flag` → `ls -la /flag` shows the
   directory contains one file named `flag` (cat on a directory fails —
   the filename is visible, the content is not).
2. `POST /audit` with `path=/flag/*` → the blacklist passes the glob, the
   shell expands `/flag/*` to `/flag/flag`, and the fixed `cat` step prints
   the flag.

## Grading discriminators
- Names the lecture's **parameter expansion** (globbing) as the bypass and
  explains that the *shell*, not the app, performs the expansion.
- Identifies the filter as an incomplete blacklist and notes that the
  command shape (`ls ... && cat ...`) is fixed — only the argument is
  attacker-controlled (argument exploitation).
- Fix: validate the path against an allowlist / resolve and confine it to
  the intended tree, or drop the shell entirely (read the file directly).
