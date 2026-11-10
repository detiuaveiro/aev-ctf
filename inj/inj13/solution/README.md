# inj13 (FaaSDeck) — intended solution & staff notes

## Path (either door)
1. **Serverless door:** `POST /functions` with `name=health`,
   `body=cat /flag/flag`; then `POST /invoke` with `name=health`,
   `input=x`. The platform runs `sh -c "echo x | cat /flag/flag"` — the
   function body is a shell pipeline, and the flag is reflected.
2. **Exec door:** `POST /exec` with `pod=web-1`, `args=cat /flag/flag`.
   The pod allowlist checks the *pod*, not the *command*; the args are
   joined into `sh -c "cd /app && cat /flag/flag"`.

## The isolation-slide connection
"Serverless" is a billing model, not a security boundary. Here every
function and every "pod exec" runs in the same process tree as the same uid
that can read `/flag/flag`. The platform's isolation claim is UI copy; the
kernel sees one user. The exec API is `kubectl exec` by construction: a
remote shell, allowlisted at the wrong layer (which container, not what it
may run).

## Grading discriminators
- Uses the function *body* as the command (not the input, which is only
  piped in) — shows they read the execution model.
- Tries or explains the exec door: pod allowlist ≠ command filter.
- Explains why "isolated environment" is false here (same uid, same
  filesystem) and what real isolation would require (separate uid/namespace,
  read-only rootfs without the flag, no shell in the exec path).

## Fix
- Invoke: run the function as data — an interpreter with a restricted API
  (or a container per function), never `sh -c` on the body.
- Exec: validate `args` against an allowlist of permitted commands with
  fixed argument shapes (what a real exec API with RBAC does), or drop the
  shell entirely (`execve` with an argument vector).
