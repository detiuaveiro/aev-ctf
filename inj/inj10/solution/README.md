# inj10 (ToolDesk) — intended solution & staff notes

## Path
1. `POST /plugins` with `name=sysdiag` and
   `script=#!/bin/sh\ncat /flag/flag` (a real newline after the shebang).
2. `POST /run` with `tool=sysdiag` → the runner executes
   `PATH=/tmp/plugins:$PATH sysdiag`; the uploaded script shadows the stock
   tool and prints the flag.

## Grading discriminators
- Explains the lecture's **command override / PATH** pattern: the attacker
  does not type the command, they control which binary a name resolves to.
- Distinguishes name validation from content control (the filter is
  correct for names and irrelevant for contents).
- Fix: run the stock tool by absolute path (or argument list, no shell),
  never prepend user-writable directories to PATH, and treat plugin uploads
  as code that requires review/signing — or do not run them as the service.
