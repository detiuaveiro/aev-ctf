# xss3 — DOM-based XSS

A team card builder: `/?card=<html>` renders a shareable profile card. The
server sends **one static page** for every parameter value; the browser's
`render()` copies the `card` URL parameter into the card element with
`innerHTML`. No server round-trip, no stored state.

## The bug

`app/app.py`, the page script: `document.getElementById('card').innerHTML =
c || DEFAULT` where `c` is the raw `?card=` parameter.

## Intended solution

Open `/?card=<img src=x onerror=grant()>`. The image fails, `onerror` fires,
`grant()` sets the `xss_grant_xss3` cookie and follows to `/flag`. Because the
sink is client-side, the payload never appears in the response body — that is
the tell that distinguishes DOM XSS from reflected XSS.

`grant()` is part of the page (a "report this card" helper) so the exploit
needs no external script.

## Verify

```
python ../../scripts/verify.py challenges/web/xss3
```
