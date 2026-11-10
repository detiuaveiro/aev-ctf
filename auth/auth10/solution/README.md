# auth10 — intended solution

- **Bug (vuln class):** user enumeration via differing login error messages
  (OWASP A07; deck slide 54; CWE-204), chained with a shared, never-rotated
  onboarding default password (deck slides 45, 48).
- **Path:**
  1. The landing page lists team members by display name only
     ("Priya Natarajan — HR Systems Administrator") and states the employee-ID
     format (first initial + last name, lowercase) — so candidate IDs are
     derivable without guessing the format.
  2. `POST /login` with a candidate ID and a throwaway password returns
     `"No such employee ID."` for an id that doesn't exist, and
     `"Incorrect password."` for one that does — confirming `pnatarajan`
     exists without needing the password.
  3. HR hands every new hire the same onboarding default (`admin123`) and
     never forces a change; the other two seeded accounts happened to
     change theirs, but `pnatarajan` never did. Trying the default against
     the confirmed ID logs in as the HR systems administrator.
  4. Only that account's `/record` page renders the "HR admin console
     token" field (the flag); the two non-admin accounts' records do not.
- **Must fail before the exploit:** confirming the ID is valid (step 2)
  alone never returns the flag — `/record` without a session redirects to
  `/login`, and a non-admin account's own `/record` has no token field.
  `solution/solve.py` checks this explicitly.
- **Correct remediation:** identical, generic error for unknown
  username/wrong password (NIST SP 800-63B); per-account, unique passwords
  enforced at onboarding, not a shared default.
- **Grading discriminators:** did the student notice the two distinct error
  strings, or just brute-force full id:password pairs (far slower, but also
  "works" — the chain is still present either way)?
- **Live perturbation for the defense:** change which `TEAM` entry is
  `admin: True` and which account still has the onboarding default; the
  solve script derives ids from the roster and tries the known default
  against every confirmed-valid id, not a hardcoded id/password pair.
