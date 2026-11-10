# inj9 (PicLink) — intended solution & staff notes

## Path
1. `POST /preview` with `url=file:///flag/flag`.
2. The proxy fetches the local file and serves its bytes (as an "image");
   the response body carries the flag.

## Grading discriminators
- Names SSRF (CWE-918) and the specific twist: an **unvalidated URL scheme**
  (file://) rather than an internal-network target.
- Explains that the *application* never reads the flag — the fetch function
  does, on the attacker's behalf.
- Fix: allowlist the scheme (http/https only), resolve and deny private /
  loopback / file targets (or drop the raw fetch and use a purpose-built
  image pipeline that only accepts image content).
