# inj11 (LogWarden) — intended solution & staff notes

## Path
1. `POST /config` with `logdir = /tmp/logs; cat /flag/flag`. The store
   validation only checks "starts with /" — a store-context check. The value
   is saved to `/tmp/config.json`.
2. `POST /ship` — the shipper reads the stored value and runs
   `sh -c "ls -la <logdir> && tail -n 5 <logdir>/app.log"`. The `;` splits
   the command; `cat /flag/flag` runs and its output is reflected.

## Why it is "second-order"
The tainted value and the execution site are different code paths, separated
by storage. The developer who wrote `/config` never thought about a shell;
the developer who wrote `/ship` trusted the config. A WAF or filter at the
input point sees a path, not a payload — the interpretation happens later,
in a context the filter was not designed for. (Same shape as the XXE hint in
the deck: stored XML re-parsed by a different component.)

## Grading discriminators
- Stores the value first and only then triggers execution (one request is
  not enough) — distinguishes understanding from reflex.
- Notices the validation is context-specific ("absolute path"), not a
  metacharacter block.
- Explains why input-side filtering is the wrong layer: the value is data at
  store time and code at execute time.

## Fix
Allowlist the logdir against a table of known directories (or resolve it and
check it is a directory prefix the shipper may use); never interpolate a
stored string into a shell — pass it as an argument vector
(`sh -c 'ls -la "$1" ...' sh <dir>`), or better, do the listing in-process.
