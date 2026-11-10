# inj2 (ShelfTag) — intended solution & staff notes

## Path
1. `POST /label` with `sku=A1` and `text` containing a real newline:
   first line anything, second line `cat /flag/flag`.
2. The blacklist strips `; | & $ \`` but passes `\n`; the unquoted newline
   ends the `printf` command and the second line runs on its own, with the
   `> /tmp/label_A1.txt && cat ...` tail — so the flag is written to (and
   echoed from) the label.

## Grading discriminators
- Identifies the filter as an **incomplete blacklist** and names the missing
  character (the newline) — the lecture's filter-evasion theme.
- Explains the mechanics (unquoted interpolation + newline = command split).
- Fix: never build a shell string — argument lists + `shell=False`, or at
  minimum treat the text as data (`printf '%s\n' "$text"` with quoting) and
  reject newlines.
