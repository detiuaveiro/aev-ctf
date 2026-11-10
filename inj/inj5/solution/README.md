# inj5 (NightPack) — intended solution & staff notes

## Path
1. `POST /backup` with `dir=catalog; cat /flag/flag`.
2. `tar` runs on `catalog` (legitimately), then the injected `cat` runs;
   the combined output is reflected and carries the flag.

## Grading discriminators
- Recognizes the lecture's **argument exploitation** pattern (a fixed
  program whose *arguments* are attacker-controlled, via a shell string).
- Explains why `exec.Command("sh", "-c", ...)` is the mistake (the shell is
  the interpreter; the argument list alone would not split).
- Fix: `exec.Command("tar", "czf", "/tmp/backup.tgz", dir)` (no shell) +
  validate/allowlist the directory.
