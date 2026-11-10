# pwn1

**Category:** pwn · **Difficulty:** intro · **Points:** 100
**Formerly:** ret2win — renamed so the name no longer hints at the leak class.

A friendly service asks for your name. It is not careful about how long a name
can be. Somewhere in the binary is a function that would happily print the flag.

**Lab address:** `nc pwn1.chal.deti 9001`  (formerly `nc ret2win.chal.deti 9001`)

```
nc pwn1.chal.deti 9001
```

Handout: `vuln` (the binary). Source is not provided to students.

## Run it locally (staff)
```bash
make build                 # produces build/vuln (the handout + solve.py needs it)
docker compose up --build  # service on localhost:9001
python solution/solve.py   # should print the flag
```
