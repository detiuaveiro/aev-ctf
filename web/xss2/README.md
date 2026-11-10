# xss2 — stored XSS

A bench log: lab members leave notes for the next shift. Notes are appended
and rendered into the page for **every** visitor without escaping.

## The bug

`app/app.py`, `index()`: `author` and `text` are interpolated into the HTML
template raw. What one person writes, every reader's browser executes.

## Intended solution

Post a note with text `<img src=x onerror=grant()>`. Reload (or wait for any
visitor): the image fails, `onerror` fires, `grant()` sets the `xss_grant_xss2`
cookie and follows to `/flag`.

`grant()` is part of the page (a "leave feedback" helper) so the exploit
needs no external script.

## Verify

```
python ../../scripts/verify.py challenges/web/xss2
```
