# sqli1 - Staff Portal: intended solution

The sign-in check in `app/app.py` (route `/login`) builds its query by
concatenation:

    SELECT id, username, role, notice FROM users
    WHERE username='<u>' AND password='<p>'

With username `admin' -- ` the query becomes

    ... WHERE username='admin' -- ' AND password='x'

so the password clause is commented out and the admin row is returned for
any password. The dashboard renders the admin row's `notice` in the
"IT announcement" card, which carries the flag.

## Reference exploit

    python solve.py [http://host:8030]
