# sqli3 - PhotoVault: intended solution

The photo detail route in `app/app.py` builds its query by concatenation:

    SELECT id, src, title, caption FROM photos WHERE id = <pid>

The query returns 4 columns, so a 4-column UNION is accepted. With:

    /photo/0 UNION SELECT 1, item, 3, secret FROM vault--

the (empty) normal result set is unioned with the hidden `vault` table.
The vault row is rendered like a photo (title "3", caption = the secret),
so the flag appears in the detail page's caption text.

## Reference exploit

    python solve.py [http://host:8032]
