# dvwa — intended solution & staff notes

## Bug
DVWA ships with a set menu of named exercises (brute force, SQLi, XSS, CSRF,
file inclusion, file upload, command injection). The intended route to a
per-student flag is completing a chosen exercise and reading the injected `FLAG`.

## Path
1. Log in (`admin / password`, or set up the DB via `/setup.php`).
2. Pick an exercise (e.g. "SQL Injection (UNION)") and set the security level.
3. Complete it and read the flag from the per-student value.

## Grading discriminators
- Did they name the vulnerability class (SQLi UNION vs blind; reflected vs stored
  XSS)?
- The write-up must include the payload and explain it — not just the output.

## Live perturbation for the defense
Raise DVWA's security level to medium/high, or disable the trivial "login"
exercise so students must use a real exploit (e.g. UNION-based SQLi).
