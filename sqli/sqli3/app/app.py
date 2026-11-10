"""PhotoVault - a small photo gallery.

Deliberately vulnerable for the course lab: the photo detail page builds
its query by concatenating the id straight out of the URL.
"""
import os
import sqlite3

from flask import Flask, render_template

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


def page(view, rows=None, photo=None, error=None):
    return render_template(
        "index.html",
        name="PhotoVault",
        tagline="A little gallery of the places we've been",
        view=view,
        rows=rows or [],
        photo=photo,
        error=error,
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


def gallery_rows():
    conn = db()
    rows = conn.execute(
        "SELECT id, title, caption, src FROM photos ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    rows = [dict(r) for r in gallery_rows()]
    for r in rows:
        r["img"] = static_img(r["src"])
    return page("gallery", rows=rows)


@app.route("/photo/<pid>")
def photo(pid):
    try:
        conn = db()
        row = conn.execute(
            f"SELECT id, src, title, caption FROM photos WHERE id = {pid}"
        ).fetchone()
        conn.close()
    except sqlite3.Error:
        row = None
    if row is None:
        return page("photo", error="That photo could not be loaded.")
    row = dict(row)
    row["img"] = static_img(row["src"])
    return page("photo", photo=row)
