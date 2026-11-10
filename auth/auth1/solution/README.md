# auth1 — intended solution

- **Bug (vuln class):** HTTP Basic authentication protected by a weak,
  never-rotated default credential (OWASP A07 — Authentication Failures;
  deck slide 24, "Base HTTP methods"; CWE-521/CWE-1392-style default
  credential).
- **Path:** `GET /` is public and carries no secret. `GET /admin` answers
  `401` with `WWW-Authenticate: Basic` to any request without the right
  credential. A short dictionary of common router default logins
  (`admin:admin`, `admin:password`, `admin:admin123`, ...) finds the shipped
  default (`admin:admin123`) in a handful of tries. The admin page's "ISP
  support token" field is the flag.
- **Must fail before the exploit:** `curl -i http://host:8060/admin` with no
  `Authorization` header, or with a wrong credential, returns `401` and no
  flag — checked explicitly by `solution/solve.py` before it tries the
  dictionary.
- **Correct remediation:** no default credential shipped; force a credential
  change on first boot; rate-limit/lock the admin console per `AGENTS.md`'s
  underlying deck guidance (slide 51).
- **Grading discriminators:** did the student guess the dictionary entry, or
  find it some other way (e.g. source leak — not present here)?
- **Live perturbation for the defense:** rotate `ADMIN_PASS` to a different
  entry in the same common-default family; the solve script's dictionary
  should still find it without being told which one.
