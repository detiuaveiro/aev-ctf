# sqli6 - Guestbook: intended solution

The form handler in `app/app.py` builds its INSERT by concatenation:

    INSERT INTO guestbook (name, message)
    VALUES ('<name>', '<message>')

With a name of:

    x', (SELECT IF(<cmp>, SLEEP(0.5), 0)) ) --

the statement becomes:

    INSERT INTO guestbook (name, message)
    VALUES ('x', (SELECT IF(<cmp>, SLEEP(0.5), 0)) ) -- ', '<message>')

(the extra `)` before the comment balances the `VALUES (` that the
comment would otherwise swallow)

- two values for two columns, so the row is accepted;
- the injected expression runs first - when `<cmp>` is true the whole
  request sleeps half a second;
- the SLEEP must sit inside the INSERT's VALUES: a trailing
  `'; SELECT SLEEP(...)` would be a second statement, which the driver
  does not execute.

`<cmp>` compares the Nth character of the hidden `vault` secret:

    (SELECT ascii(substring(secret,N,1)) FROM vault LIMIT 1) > M

A sentinel comparison (`... IS NOT NULL AND ... > 0`) detects the end of
the secret; binary-searching M (7 requests per character) reconstructs
the flag. Expect the full solve to take on the order of a minute.

## Reference exploit

    python solve.py [http://host:8035]
