# auth11 — intended solution

- **Bug (vuln class):** password-reset token is predictable, non-expiring,
  and reusable (OWASP A07; deck slide 54).
- **Path:** every page's footer names `postmaster@inboxnow.local` as the
  contact for sign-in trouble. The reset token is
  `sha256("reset:" + username)[:20]` — the same value forever, derivable
  from the username alone, with no secret or timestamp involved. Computing
  it for `postmaster` and `GET /reset/<token>` reaches a form to set that
  mailbox's password directly; signing in then reads the flag from its
  inbox. The legitimate `/forgot` flow for the seeded `user` account is
  never needed — it only demonstrates the token's shape: the page shows
  "a reset link has been sent to your email address" and leaves the
  actual link hidden in the page source (`display: none`).
- **Must fail before the exploit:** `/mailbox` with no session redirects
  to login, and the token computed for `user` only ever resets `user`'s
  own password — checked explicitly by `solution/solve.py` before it
  computes `postmaster`'s token.
- **Correct remediation:** reset tokens must be random (not derived from
  the username), single-use, short-lived, and stored hashed server-side,
  bound to the specific request that created them.
- **Grading discriminators:** did the student notice the token never
  changes between requests for the same username, i.e. that it carries no
  randomness or timestamp at all?
- **Live perturbation for the defense:** `postmaster`'s starting password
  is randomized every process start (`os.urandom(16).hex()`) specifically
  so the exploit can't work by guessing a default — only by reaching the
  token-based reset.
