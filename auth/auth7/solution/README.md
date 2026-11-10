# auth7 — intended solution

- **Bug (vuln class):** JWT verification trusts the token's own `alg`
  header and accepts `"none"` (OWASP A07; deck slides 42–43, 56).
- **Path:** logging in as the seeded `acme` partner shows the normal
  three-part `header.payload.signature` token shape. The verifier branches
  on the submitted token's `alg` field; supplying a token with
  `{"alg":"none","typ":"JWT"}` as the header, `{"partner":"admin"}` as the
  payload, and an empty signature segment is accepted without any
  signature check, because the code path for `alg == "none"` skips
  verification entirely. `GET /partner/admin` with that token as
  `Authorization: Bearer <token>` returns the flag.
- **Must fail before the exploit:** the legitimately-issued `acme` token
  (valid HS256 signature, `partner: acme`) against `/partner/admin`
  returns `403` — checked explicitly by `solution/solve.py` before it
  crafts the forged token.
- **Correct remediation:** the verifier must pin the expected algorithm
  itself (e.g. always verify as HS256) and never read `alg` from the
  token to decide how to check it; reject `"none"` outright.
- **Grading discriminators:** did the student craft the forged token by
  hand (base64url three-part construction), or find a library that lets
  `alg: none` through unprompted?
- **Live perturbation for the defense:** rotate `JWT_SECRET`; the forged
  `alg: none` token needs no knowledge of the secret at all, so the
  exploit is unaffected either way — a useful point to probe in grading
  (does the student understand *why* it still works?).
