# auth9 — intended solution

- **Bug (vuln class):** session token derived from a predictable timestamp
  (OWASP A07; deck slide 59; CWE-330/331).
- **Path:** every login (including the on-call rotation service's admin
  integration account) mints `token = sha1(f"{user}:{unix_ts}")`. The
  public `/bot/refresh-oncall` endpoint triggers an admin re-auth at a
  timestamp the caller can bound tightly (their own clock, +/- a few
  seconds of latency) without ever revealing the token. On the agent
  queue page both halves are surfaced: the *Rotate on-call now* button (a form
  POST to /bot/refresh-oncall) and the *Admin ticket queue* link
  (/ticket/admin). Recomputing the
  hash for every timestamp in that narrow window and presenting each as
  the `token` cookie against `/ticket/admin` finds the one that validates.
- **Must fail before the exploit:** a guessed/own token against
  `/ticket/admin` returns `403` — checked explicitly by
  `solution/solve.py` before it triggers the refresh and brute-forces the
  window.
- **Correct remediation:** derive session tokens from a cryptographically
  secure random generator (>=128 bits), never from a timestamp or other
  guessable input.
- **Grading discriminators:** did the student notice the token is
  deterministic from username + time, or try to brute-force the full
  40-character SHA-1 space (infeasible) instead of the actual ~10-second
  window?
- **Live perturbation for the defense:** the exact token is never fixed
  (minted fresh at whatever instant the request is processed); the solve
  script derives its search window from its own clock at call time, not a
  hardcoded timestamp.
