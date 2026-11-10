# auth8 — intended solution

- **Bug (vuln class):** JWT signed with a weak, brute-forceable HMAC
  secret (OWASP A07; deck slides 42, 56). The signature check itself is
  correct — contrast with `auth7`'s `alg: none` hole.
- **Path:** logging in as the seeded `customer` account returns the normal
  banking dashboard; the valid `role: customer` HS256 token is not printed on
  the page — it is delivered in a `token` cookie (the login response's
  `Set-Cookie` header, or the browser's cookie jar), so read it from there. The signing secret is a 4-digit numeric
  string (10,000 possibilities) — offline, trying every candidate against
  the sample token's own signature (recomputing
  `HMAC-SHA256(candidate, header.payload)` and comparing to the token's
  signature bytes) finds it in well under a second. With the secret
  recovered, forging a fresh token with `role: admin` and the correct
  signature is a few lines. `GET /accounts/admin` with the forged token
  returns the flag.
- **Must fail before the exploit:** the legitimately-issued `customer`
  token against `/accounts/admin` returns `403` — checked explicitly by
  `solution/solve.py` before it brute-forces the secret.
- **Correct remediation:** HMAC secrets must be long, random, and kept
  server-side only (>=256 bits for HS256); never a human-memorable or
  small-keyspace value.
- **Grading discriminators:** did the student brute-force the full secret
  space methodically, or guess a specific weak value by luck? (Either
  recovers it here, since the keyspace is small enough for both.)
- **Live perturbation for the defense:** the secret is randomized fresh
  every process start (`random.randint(0, 9999)`); the solve script must
  actually run the brute-force against the live sample token, not reuse a
  cached secret.
