# auth12 — intended solution

- **Bug (vuln class):** credential store reachable in a reversible
  (base64, mislabelled "encrypted") form via an exposed static export
  (OWASP A07; deck slides 46, 49; CWE-257/CWE-522).
- **Path:** nothing on the real site links to the export. `GET /robots.txt`
  carries a `Disallow: /export/` entry (advisory only, same lesson as the
  infoleak suite's leak8 — a crawler courtesy, not access control).
  `GET /export/` has directory listing enabled and shows
  `cornerstone_staging.sql.bak` next to a couple of ordinary neighbours
  (`.htaccess`, `README.txt`). The backup contains the admin row with a
  `password_encrypted` column — base64 of the real password. Decoding it
  and logging in at `/login` as `admin` reaches `/dashboard`, which shows
  the flag.
- **Must fail before the exploit:** the export itself, fetched directly,
  contains no `flag{` string (only the encoded password); `/dashboard`
  without a session redirects to `/login` — both checked explicitly by
  `solution/solve.py` before it decodes the password and logs in.
- **Correct remediation:** never publish a database export at a guessable
  or indexed path; store passwords only as a slow, salted hash (Argon2id/
  bcrypt/scrypt/PBKDF2), never a reversible encoding.
- **Grading discriminators:** did the student recognize base64 is not
  encryption, or assume the "encrypted" label and stop?
- **Live perturbation for the defense:** the admin password is randomized
  every process start (`os.urandom(9)`, base64-encoded) when not
  overridden by env; the solve script must decode the live export's value,
  not reuse a cached password.
