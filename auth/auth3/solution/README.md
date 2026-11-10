# auth3 — intended solution

- **Bug (vuln class):** session/authorization token carried in the URL
  (OWASP A07; deck slides 29–30, 37) — it leaks wherever URLs do: browser
  history, referrer headers, and here, into a public testimonial page a
  support agent pasted it into.
- **Path:** the tester's own tracking link (`/track?sid=<guest_sid>`) is
  handed out on the landing page and never shows the flag — it belongs to a
  non-VIP parcel. `/stories` is a public "customer testimonials" page that
  quotes a VIP customer's message, which includes their full tracking link
  verbatim. Following that link's `sid` reaches a parcel flagged `vip`,
  whose tracking page renders a "concierge support token" field — the flag.
- **Must fail before the exploit:** the tester's own `sid` and any guessed
  `sid` return `vip: false` or "not found" — checked explicitly by
  `solution/solve.py` before it reads `/stories`.
- **Correct remediation:** don't use a bare identifier in the URL as the
  sole authorization check for a sensitive resource; if a link must be
  shareable, scope it narrowly and never quote it verbatim in public
  content.
- **Grading discriminators:** did the student notice their own sid never
  shows a token, prompting them to look elsewhere (the public pages) for a
  different one?
- **Live perturbation for the defense:** the VIP/guest sids are regenerated
  randomly on every process start (`secrets.token_hex(8)`); the solve script
  must read the leaked link out of the live `/stories` page, not a
  hardcoded value.
