# leak3 (formerly leak-dir-listing) -- intended solution & staff notes

Directory listing is enabled and a flag file is in plain sight.

## Path
1. Bring the service up.
2. Run the reference exploit `python solution/solve.py` (or follow the steps
   in the solve script).
3. The solve prints the flag.

## Grading discriminators
- Did they identify the specific *information-disclosure* class at play, not a
   generic 'hack the server'?
- The write-up should name the precise leak (source comment, verbose error,
   directory listing, backup file, JWT payload, git history, debug route,
   IDOR/verbose serialization, or oracle) and the remediation (remove debug
   artifacts, hide stack traces, disable listing, scrub backups, stop putting
   secrets in tokens, don't serve .git, gate debug routes, enforce object-level
   auth, and make oracle endpoints constant-time).
