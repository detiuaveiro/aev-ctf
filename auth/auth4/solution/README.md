# auth4 — intended solution

- **Bug (vuln class):** server-side authorization decision made from a
  client-controlled value (OWASP A07; deck slide 19 "there is no
  client-side security model" / slide 5; CWE-602 — client-side enforcement
  of server-side security).
- **Path:** logging in as the seeded `employee` account sets a real
  server-side session **and** a plain, readable-and-writable `role=employee`
  cookie. The "Manager console" link is an always-visible nav item (no
  client-side hiding), so the employee both sees the manager area and is
  refused with `403` when they click it. `GET /manager` requires a session
  (so an anonymous visitor is redirected to login) but then checks role by
  reading that same client-writable cookie — not the session's actual stored
  role. Editing the cookie to `role=manager` and requesting `/manager` again,
  still as the logged-in employee, returns the flag.
- **Must fail before the exploit:** `/manager` with the unmodified
  `role=employee` cookie (normal post-login state) returns `403` — checked
  explicitly by `solution/solve.py` before it edits the cookie.
- **Correct remediation:** never branch a security decision on a value the
  client can set; store role in the server-side session store and read it
  from there only.
- **Grading discriminators:** did the student find this by reading the
  response headers/cookies (noting the `role` cookie is plain and writable)
  rather than assuming the `403` they got as `employee` is the final answer?
- **Live perturbation for the defense:** rename the cookie or the required
  value; the solve script edits whatever cookie the login response actually
  sets, rather than a hardcoded name.
