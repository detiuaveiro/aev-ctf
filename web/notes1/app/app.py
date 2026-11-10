"""notes1 (formerly idor-notes) -- an insecure-direct-object-reference challenge.

Users log in and read their own notes at /note/<id>. The endpoint checks that
you are authenticated but NOT that the note belongs to you: the bug. The admin's
private note holds the flag. Intended solution: log in as the provided low-priv
user, then walk note ids until you read the admin's.

The flag is read from the environment (FLAG) so it is injected per student and
never lives in the source or the image.
"""
import os

from flask import Flask, abort, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = os.urandom(32)

FLAG = os.environ.get("FLAG", "flag{idor_local_test}")

# id -> (owner_username, title, body). Note 3 is the admin's; it holds the flag.
NOTES = {
    1: ("guest", "Shopping", "milk, eggs, coffee"),
    2: ("guest", "Todo", "finish the lab report"),
    3: ("admin", "DO NOT SHARE", FLAG),
    4: ("alice", "Ideas", "a startup that delivers ice"),
}
USERS = {"guest": "guest123"}  # the credentials students are given


@app.route("/")
def index():
    who = session.get("user")
    if not who:
        return ('<h1>Notes</h1><form method=post action=/login>'
                'user <input name=user> pass <input name=pw type=password>'
                '<button>login</button></form>')
    links = "".join(f'<li><a href="/note/{i}">note {i}{" \U0001F512" if NOTES[i][0] == "admin" else ""}</a></li>' for i in NOTES)
    return f"<h1>Hi {who}</h1><ul>{links}</ul>"


@app.route("/login", methods=["POST"])
def login():
    u, p = request.form.get("user"), request.form.get("pw")
    if USERS.get(u) == p:
        session["user"] = u
        return redirect(url_for("index"))
    abort(401)


@app.route("/note/<int:note_id>")
def note(note_id):
    if "user" not in session:
        abort(401)                     # authentication IS checked...
    if note_id not in NOTES:
        abort(404)
    owner, title, body = NOTES[note_id]
    # ...but authorization is NOT. No `owner == session['user']` check. The bug.
    return f"<h2>{title}</h2><pre>{body}</pre><small>owner: {owner}</small>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
