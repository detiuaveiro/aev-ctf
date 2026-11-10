# auth5 — intended solution

- **Bug (vuln class):** session fixation — the session identifier is not
  regenerated at login (OWASP A07; deck slides 60–62; CWE-384).
- **Path:** `GET /` mints a pre-login `sid` cookie for guest browsing. The
  landing page's "registrar's link checker" form posts to
  `/helpdesk/verify-link`; the bot (standing in for the deck's "Alice clicks
  the link and logs on") opens the link **as the caller's own session** —
  the `sid` cookie that travels with the request — and authenticates the
  advisor role under it **without rotating it**. A visitor who submits the
  form ends up holding a now-authenticated session: `GET /dashboard` with
  the original cookie returns the flag.
- **Must fail before the exploit:** `/dashboard` with a fresh `sid` that
  was never passed to `/helpdesk/verify-link` redirects to `/` — checked
  explicitly by `solution/solve.py` before it calls the bot.
- **Correct remediation:** issue a brand-new session identifier on every
  privilege change (login, role elevation); never accept a client-supplied
  identifier as already valid (strict session mode).
- **Grading discriminators:** did the student realize the pre-login `sid`
  is reusable at all, i.e. that nothing distinguishes a guest session from
  one eligible to become authenticated?
- **Live perturbation for the defense:** this is inherent to the identifier
  model (any sid works the same way) — no per-run randomization is needed
  beyond what already exists (`secrets.token_hex(16)` per session).
