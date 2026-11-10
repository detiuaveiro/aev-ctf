# mutillidae — intended solution & staff notes

## Bug
Mutillidae ships with labs across the OWASP Top 10 (SQLi, XSS, CSRF, SSRF,
broken auth, insecure deserialization, XXE, command injection). The intended
route to a per-student flag is completing a chosen lab and reading the injected
`FLAG`.

## Path
1. Browse to the app and pick a lab (e.g. "SQL Injection - Extract Data").
2. Complete the lab per its instructions.
3. Read the flag from the per-student value.

## Grading discriminators
- Did they name the vulnerability class and explain the exploit precisely?
- The write-up must describe the payload and why it works.

## Live perturbation for the defense
Enable Mutillidae's "hints" off / set a harder lab so students must chain
vulnerabilities rather than follow the walkthrough.
