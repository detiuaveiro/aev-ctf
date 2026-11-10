# bwapp — intended solution & staff notes

## Bug
bWAPP ships with 100+ exercises, each a named vulnerability (SQL injection,
XSS, CSRF, SSRF, insecure upload, XXE, …). The intended route to a per-student
flag is completing a chosen exercise and reading the injected `FLAG`.

## Path
1. Log in (bWAPP's default `bee / bug`).
2. Pick an exercise (e.g. "SQL Injection (GET/Search)").
3. Complete it and read the flag from the per-student value.

## Grading discriminators
- Did they pick a *named* vulnerability class and explain the exploit precisely
  (e.g. "UNION-based SQLi")?
- The write-up must describe the payload and why it works, not just paste output.

## Live perturbation for the defense
Disable the "easy" exercises (login bypass, default creds) so students must use
a real exploit (e.g. blind SQLi or SSRF).
