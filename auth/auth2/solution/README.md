# auth2 — intended solution

- **Bug (vuln class):** access control decision based on the client-supplied
  `Referer` header (OWASP A07; deck slides 33–36; CWE-293 — trusting a
  client-controlled value for a security decision).
- **Path:** `GET /wiki/internal/ops-runbook` checks that the `Referer`
  header contains `/wiki/staff-home`. No session, cookie, or role is ever
  checked. Sending the header directly (`curl -H "Referer: http://host/wiki/staff-home"`)
  reaches the page without ever visiting `/wiki/staff-home` first.
- **Must fail before the exploit:** a request to `/wiki/internal/ops-runbook`
  with no (or a wrong) `Referer` returns `403` and no flag — checked
  explicitly by `solution/solve.py` before it sends the forged header.
- **Correct remediation:** authenticate staff with a real session/role
  check; never use `Referer` for access control (it is advisory, per RFC
  7231 §5.5.2, and client-omittable).
- **Grading discriminators:** did the student notice they never logged in
  anywhere, i.e. that the "staff-only" wall had nothing behind it?
- **Live perturbation for the defense:** rename `STAFF_HOME`/the runbook
  path; the solve script should still work by reading the real staff-home
  path out of the landing page's link, not a hardcoded string.
