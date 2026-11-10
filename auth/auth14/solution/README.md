# auth14 — intended solution

- **Bug (vuln class):** logout invalidates only the client-side cookie, not
  the server-side session record (OWASP A07; deck slide 64; CWE-613 —
  insufficient session expiration).
- **Path:** every visitor is signed in as an ordinary customer — the first
  visit mints a `sid` cookie and the dashboard displays it ("Signed in as
  personal banking customer"). The nightly monitoring probe
  (`/bot/manager-shift-report`, triggerable from the Branch staff panel)
  signs the branch manager in, pulls the report, then "logs out" — but the
  session record stays valid server-side; only the probe's own cookie is
  discarded. The public `/diagnostics` page (a secondary, smaller flaw —
  verbose debug logging) lists the probe's session ids, including the
  now-"logged-out" manager one. Swapping your own `sid` cookie for that id
  authenticates you as the manager — the classic session pivot from a
  low-privilege session you hold to a higher-privilege one you should not.
- **Must fail before the exploit:** the customer dashboard carries no
  `flag{` string and shows "Manager console: not available" — checked
  explicitly by `solution/solve.py` (which also asserts its own cookie was
  issued) before it reads `/diagnostics`. Note the swap must REPLACE the
  cookie value; adding a second `sid` does nothing.
- **Correct remediation:** logout must invalidate the session **server
  -side** (delete or mark the record), not just clear the client's cookie;
  separately, session identifiers should never appear in a
  diagnostic/debug log reachable without authentication.
- **Grading discriminators:** did the student notice logout only ever
  touches the client — i.e., that there's no server-side session store
  mutation on logout at all in this app?
- **Live perturbation for the defense:** the probe's sid is freshly random
  (`secrets.token_hex(16)`) every run and only the last 20 diagnostics
  entries are kept; the solve script reads the live log rather than a
  hardcoded value.
