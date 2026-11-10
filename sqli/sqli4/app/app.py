"""DropLite - a tiny file transfer service.

Deliberately vulnerable for the course lab: the file search builds its
query by concatenating the search term straight from the request. The
service shows names and sizes, never contents.
"""
import os
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)

DB_PATH = "/var/lib/app/app.db"

KB = 1024


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def static_img(*candidates):
    for c in candidates:
        if os.path.exists(os.path.join(app.static_folder, "img", c)):
            return f"/static/img/{c}"
    return None


def human_size(n: int) -> str:
    if n >= KB:
        return f"{n / KB:.1f} KB"
    return f"{n} B"


def with_sizes(rows):
    out = []
    for r in rows:
        r = dict(r)
        r["size_label"] = human_size(r["size"])
        out.append(r)
    return out


def all_files():
    conn = db()
    rows = conn.execute(
        "SELECT id, name, size FROM files ORDER BY id"
    ).fetchall()
    conn.close()
    return with_sizes(rows)


def page(view, rows=None, q=None, matches=None):
    return render_template(
        "index.html",
        name="DropLite",
        tagline="Send a file, get a link, done.",
        view=view,
        rows=rows or [],
        q=q or "",
        matches=matches or [],
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/")
def index():
    return page("home", rows=all_files())


@app.route("/search")
def search():
    q = request.args.get("q", "")
    try:
        conn = db()
        rows = conn.execute(
            f"SELECT id, name, size FROM files WHERE name LIKE '%{q}%' ORDER BY id"
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        rows = []
    return page("search", q=q, matches=with_sizes(rows))
