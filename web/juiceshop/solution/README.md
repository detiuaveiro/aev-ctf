# juiceshop — intended solution & staff notes

## Bug
Juice Shop ships with ~100+ challenges across the OWASP Top 10. The intended
route for a per-student flag is the **Score Board** challenge family — find the
hidden score board, complete a small set of challenges, and the flag is the
per-student `FLAG` value injected at deploy time.

## Path
1. Discover the hidden `/score-board` route (e.g. inspect the JS bundle or use the
   search/API).
2. Complete the introductory challenges (e.g. "Log in with the administrator's
   user credentials", "Score Board").
3. Read the flag from the per-student challenge that returns `FLAG`.

See the upstream project's README for the full challenge list. CI does a smoke
test (app responds, flag env present), not a full solve.

## Grading discriminators
- Did they map a chosen exploit to the correct OWASP category (SQLi vs XSS vs
  IDOR)? Naming the class precisely is the learning objective.
- The write-up must explain *why* the chosen challenge is exploitable, not just
  "I clicked the score board".

## Live perturbation for the defense
Enable the "cutting corners"/harder challenges or restrict the score board route
so students must chain two vulnerabilities.
