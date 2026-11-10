"""Linkly - paste a link, we preview it for you.

Deliberately vulnerable for the course lab: the preview page builds its
query by concatenating the id straight from the URL, and the app fetches
every link it renders.
"""
import os
import sqlite3
import time

import requests
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

DB_PATH = "/var/lib/app/app.db"
FETCH_TIMEOUT = 6


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def static_img(*candidates):
    for c in candidates:
        if os.path.exists(os.path.join(app.static_folder, "img", c)):
            return f"/static/img/{c}"
    return None


def preview(url: str) -> str:
    t0 = time.monotonic()
    try:
        r = requests.get(url, timeout=FETCH_TIMEOUT, allow_redirects=False)
        return f"Fetched: HTTP {r.status_code} in {int((time.monotonic() - t0) * 1000)} ms"
    except requests.RequestException:
        return "Couldn't reach that link."


def recent_links():
    conn = db()
    rows = [dict(r) for r in conn.execute(
        "SELECT id, url, note FROM links ORDER BY id DESC LIMIT 5"
    ).fetchall()]
    conn.close()
    return rows


def by_id(n: str):
    conn = db()
    rows = [dict(r) for r in conn.execute(
        f"SELECT url, note, id FROM links WHERE id = {n}"
    ).fetchall()]
    conn.close()
    return rows


def page(view, links=None, previews=None):
    return render_template(
        "index.html",
        name="Linkly",
        tagline="Paste a link - we fetch it and preview it for you",
        view=view,
        links=links or [],
        previews=previews or [],
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/")
def index():
    return page("home", links=recent_links())


@app.route("/add", methods=["POST"])
def add():
    u = request.form.get("url", "").strip()
    note = request.form.get("note", "").strip()
    if not u:
        return redirect("/")
    conn = db()
    cur = conn.execute("INSERT INTO links (url, note) VALUES (?, ?)", (u, note))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return redirect(f"/l/{new_id}")


@app.route("/l/<path:n>")
def link(n):
    try:
        rows = by_id(n)
    except sqlite3.Error:
        rows = []
    previews = [{
        "url": r["url"],
        "note": r["note"],
        "status": preview(r["url"]),
    } for r in rows]
    return page("preview", previews=previews)
