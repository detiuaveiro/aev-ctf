# auth6 — intended solution

- **Bug (vuln class):** session fixation delivered via an overbroad,
  shared-domain cookie scope (OWASP A07; deck slide 63 — the
  "evil.server.com plants a cookie for *.server.com, good.server.com
  trusts it" scenario).
- **Path:** the app's home page links to the company's marketing microsite
  (one company, two sites, one shared cookie). The microsite is reached by
  pointing the client at `marketing.auth6.chal.deti` — in the lab that's a
  normal link on the home page (the `*.chal.deti` wildcard resolves it to the
  same box) or, with curl, a `Host: marketing.auth6.chal.deti` header; the
  container branches on the `Host` header to play both vhosts. Its
  `/plant` "leave a comment / remember you" form sets the shared `sid` cookie
  to any value the visitor supplies. The real app's `/dashboard` shows the
  visitor their own `sid` (surfacing that the two sites share one session),
  and the `/helpdesk/verify-link` bot (same mechanic as `auth5`) signs the
  manager in under whatever `sid` arrives, without rotating it. An attacker
  plants a known `sid` via the microsite, has the bot authenticate it, then
  presents that same `sid` to the real app's `/dashboard`.
- **Must fail before the exploit:** a `sid` planted but never run through
  `/helpdesk/verify-link` returns no flag from `/dashboard` (redirects to
  the app landing page) — checked explicitly by `solution/solve.py`.
- **Correct remediation:** never scope a session cookie wider than the one
  origin that needs it (no `Domain=` at all, or scope to the exact app
  host only); rotate the session id on every login regardless of delivery
  path.
- **Grading discriminators:** did the student realize the microsite and
  the app share a cookie at all, i.e. look at the microsite's own requests
  instead of only the app's?
- **Live perturbation for the defense:** none needed beyond what already
  varies (the `sid` is attacker-chosen either way); if a real second vhost
  is added later, `is_marketing()`'s hostname check is the only thing that
  would need updating.
