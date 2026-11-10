# inj4 (Catalogo) — intended solution & staff notes

## Path
1. `POST /import` with an XML document whose DOCTYPE declares an external
   entity over `file:///flag/flag`, referenced in the record.
2. The parsed record text is reflected on the page (and kept in "Recent
   imports"), carrying the flag.

## Grading discriminators
- Names XXE (CWE-611) and explains the mechanics: the parser resolves
  `SYSTEM "file://..."` entities because no security features were set.
- Distinguishes direct entity reflection from parameter entities / blind XXE
  (this one is direct).
- Fix: `DocumentBuilderFactory` with `disallow-doctype-decl` (or at least
  `external-general-entities=false` + `external-parameter-entities=false`),
  or a parser that does not need DTDs at all.
