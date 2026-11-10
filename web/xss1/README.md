# xss1 — reflected XSS

A recipe search box. `/?q=<term>` filters the corpus and renders the query
back into the results header (and the input's `value` attribute) without
escaping — classic reflected XSS.

## The bug

`app/app.py`, `index()`: `q` is interpolated into the HTML template raw.

## Intended solution

Open `/?q=<img src=x onerror=grant()>`. The image fails to load, `onerror`
fires, `grant()` sets the `xss_grant_xss1` cookie and follows to `/flag`, which
answers with the flag for any request carrying that cookie.

`grant()` is part of the page (a "share result" helper) so the exploit needs
no external script.

## Verify

```
python ../../scripts/verify.py challenges/web/xss1
```
