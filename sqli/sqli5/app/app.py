"""The Daily Byte - a small blog from the lab.

Deliberately vulnerable for the course lab: the tag filter builds its
query by concatenating the term straight from the request.
"""
import os
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)

DB_PATH = "/var/lib/app/app.db"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def static_img(*candidates):
    for c in candidates:
        if os.path.exists(os.path.join(app.static_folder, "img", c)):
            return f"/static/img/{c}"
    return None


def recent():
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT id, title, tag, posted FROM posts ORDER BY id DESC LIMIT 6"
    ).fetchall()]
    conn.close()
    return rows


def tag_counts():
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT tag, COUNT(*) AS n FROM posts GROUP BY tag ORDER BY tag"
    ).fetchall()]
    conn.close()
    return rows


def by_tag(t: str):
    conn = db()
    rows = [dict(r) for r in conn.execute(
        f"SELECT id, title, tag, posted FROM posts WHERE tag='{t}' ORDER BY id DESC"
    ).fetchall()]
    conn.close()
    return rows


def page(tag=None, posts=None, tags=None):
    return render_template(
        "index.html",
        name="The Daily Byte",
        tagline="Notes from the people who keep the lab running",
        tag=tag or "",
        posts=posts or [],
        tags=tags or [],
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/")
def index():
    t = request.args.get("tag")
    if t is not None:
        try:
            posts = by_tag(t)
        except sqlite3.Error:
            posts = []
        return page(tag=t, posts=posts, tags=tag_counts())
    return page(posts=recent(), tags=tag_counts())
