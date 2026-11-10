# notes1 (formerly idor-notes) — intended solution & staff notes

## Bug
`/note/<id>` checks authentication (`"user" in session`) but never checks
**authorization** — it does not verify the note's `owner` matches the logged-in
user. Classic IDOR / broken object-level authorization (OWASP API1).

## Path
1. Log in as `guest / guest123`.
2. The dashboard links notes 1–4. Request each `/note/<id>`; note 3 is owned by
   `admin` and returns the flag.
3. Iterating ids is the whole trick — a `curl` loop with the session cookie is
   enough.

See `solve.py`. CI runs it on every push.

## Grading discriminators
- Did they identify it as *broken authorization* specifically, not "no login"
  (auth IS enforced)? Naming the class precisely is the learning objective.
- The remediation must be an ownership check at the object level
  (`owner == session['user']`), not "hide the link" or "use UUIDs" — press on
  this in the write-up; obscuring the id is the common wrong answer.

## Live perturbation for the defense
Add a second low-priv user and make the admin note owned by a *non-sequential*
id (e.g. 9182), or switch ids to UUIDs. The student must now find another way to
enumerate (a listing endpoint, an id leaked elsewhere) — tests whether they
understood the vuln class or just guessed `3`.
