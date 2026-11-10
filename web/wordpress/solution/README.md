# wordpress — intended solution & staff notes

## Bug
The site runs stock **WordPress 6.9.4** (vulnerable range: 6.8.x < 6.8.6,
6.9.x < 6.9.5, 7.0.x < 7.0.2; fixed in 6.8.6 / 6.9.5 / 7.0.2). That core
carries the unauthenticated **wp2shell** RCE chain:

- **CVE-2026-63030** (CVSS 9.8) — REST API `/batch/v1` route confusion: a
  double-nested batch desyncs the sub-request dispatch so a nested
  `requests` body is treated as top-level batch entries.
- **CVE-2026-60137** — WP_Query `author__not_in` not sanitised: with the
  confusion in place, an untrusted `author_exclude` query param reaches
  `author__not_in` raw → UNION/time-based SQLi.

## Path
1. Time-based SQLi probe through the confused batch (`SLEEP` oracle).
2. UNION row forgery in `wp_posts`: seed oEmbed cache rows, then forge
   `customize_changeset` + request-hook rows so a `POST /wp/v2/users` is
   dispatched in the real admin's context → new administrator account.
3. Log in as the forged admin; upload a one-shot plugin whose REST route
   runs `passthru()` (then deactivates and unlinks itself).
4. Read the flag: it is materialized at `/etc/lab_flag` — outside the web
   root, and the DB user has no `FILE` privilege, so only the RCE can read
   it. `cat /etc/lab_flag` is the reference command.

## Grading discriminators
- Did they identify the core-version requirement (and ideally BOTH CVEs)?
- The write-up must explain the batch dispatch confusion and the
  `author__not_in` sink — not just "ran a PoC".

## Live perturbation for the defense
Upgrade the core to 6.9.5+ / 7.0.2 — the chain dies at step 1.
