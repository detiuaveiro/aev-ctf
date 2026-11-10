# inj4

**Category:** inj · **Difficulty:** medium · **Points:** 150

A library catalogue import that "accepts standard XML". What counts as
standard depends on how carefully the parser was configured — this one was
configured with the default.

**Lab address:** http://inj4.chal.deti:8043

## Run it locally (staff)
```bash
docker compose up --build   # http://localhost:8043
python solution/solve.py    # should print the flag (raw-XML body)
python solution/ui_check.py # same via the browser's form path (bug 2026-10-30:
                            # the form posted urlencoded 'xml' and the server
                            # parsed the raw body -> "prolog" parse error)
```
