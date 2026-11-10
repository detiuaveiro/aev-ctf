# auth13 — intended solution

- **Bug (vuln class):** no rate limiting on the login endpoint (OWASP A07;
  deck slides 45, 47, 51; CWE-307), combined with a low-entropy seeded
  password drawn from a common/short list.
- **Path:** `POST /login` accepts unlimited attempts with no delay, lockout,
  or per-IP/per-account throttling. A short dictionary of the most-used
  passwords in the world (`qwerty` sits near the top of every such list)
  finds `vpnuser`'s password in a handful of tries; `/dashboard` then
  returns the flag.
- **Must fail before the exploit:** `/dashboard` with no session redirects
  to `/login`, and a wrong-password attempt never returns the flag —
  checked explicitly by `solution/solve.py` before it runs the dictionary.
- **Correct remediation:** rate-limit authentication (progressive delay
  preferred over hard lockout, to avoid a denial-of-service vector);
  monitor for repeated failures; never seed a low-entropy password even
  for a "test" account.
- **Grading discriminators:** did the student notice the absence of any
  delay/lockout across repeated failed attempts, or just happen to guess
  the password on the first try?
- **Live perturbation for the defense:** rotate `VPNUSER_PASSWORD` to
  another top-of-the-list password (another keyboard pattern, or the next
  most-used entry); the solve script's dictionary should still find it
  without being told which one.
