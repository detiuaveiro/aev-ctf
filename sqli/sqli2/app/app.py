"""TechBazaar Search - a small parts counter.

Deliberately vulnerable for the course lab: the search builds its query
by concatenating the term straight from the request, and database
errors are shown to the user as-is.
"""
import os
import pymysql

from flask import Flask, render_template, request

app = Flask(__name__)

DB_CONFIG = dict(
    host="127.0.0.1",
    user="app",
    password="apppass",
    database="appdb",
    charset="utf8mb4",
)


def db():
    return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **DB_CONFIG)


def static_img(*candidates):
    for c in candidates:
        if os.path.exists(os.path.join(app.static_folder, "img", c)):
            return f"/static/img/{c}"
    return None


def money(v) -> str:
    return f"\u20ac{float(v):.2f}"


app.jinja_env.globals["money"] = money


def query(sql: str):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def featured():
    return query(
        "SELECT id, name, price, description FROM products ORDER BY id LIMIT 6"
    )


def page(view, rows=None, q=None, matches=None, error=None):
    return render_template(
        "index.html",
        name="TechBazaar Search",
        tagline="The little parts counter on Canal Street",
        view=view,
        rows=rows or [],
        q=q or "",
        matches=matches or [],
        error=error,
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/")
def index():
    return page("home", rows=featured())


@app.route("/search")
def search():
    q = request.args.get("q", "")
    try:
        matches = query(
            f"SELECT id, name, price, description FROM products "
            f"WHERE name LIKE '%{q}%' ORDER BY id"
        )
        error = None
    except pymysql.Error as e:
        matches = []
        error = f"Search failed: {e}"
    return page("search", q=q, matches=matches, error=error)
