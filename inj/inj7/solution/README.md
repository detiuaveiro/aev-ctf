# inj7 (DeskOne) — intended solution & staff notes

## Path
1. `POST /ticket` with `requester=x$(cat /flag/flag)` (the sanitizer strips
   `; | &`, so `$(...)` is the surviving injection form).
2. The shell expands the substitution while appending the log line — the
   flag is written into the desk log.
3. `GET /log` shows the log tail, which now carries the flag.

## Grading discriminators
- Explains where the flag *lives* (the log file, not any response) and why
  the /ticket page itself shows nothing.
- Names the root cause: building a shell command (here even a log line)
  from untrusted input — logging via a shell instead of the logging library.
- Fix: write logs with the logging module / file API (no shell); if a
  shell is unavoidable, never interpolate — pass data as arguments.
