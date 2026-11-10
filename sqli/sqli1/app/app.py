"""Staff Portal - on-shift sign-in for the IT support crew.

Deliberately vulnerable for the course lab: the sign-in check builds its
SQL query by concatenating form input (no parameterisation, no escaping).
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


def page(user=None, error=None, rows=None, announcement=None):
    return render_template(
        "index.html",
        name="Staff Portal",
        tagline="On-shift sign-in for the IT support crew",
        user=user,
        error=error,
        rows=rows or [],
        announcement=announcement,
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


def roster():
    conn = db()
    rows = conn.execute(
        "SELECT username, role FROM users ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    return page()


@app.route("/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    try:
        conn = db()
        row = conn.execute(
            "SELECT id, username, role, notice FROM users "
            f"WHERE username='{u}' AND password='{p}'"
        ).fetchone()
        conn.close()
    except sqlite3.Error:
        return page(error="Something went wrong on our side - please try again.")
    if row is None:
        return page(error="That name and password do not match our roster.")
    return page(
        user={"username": row["username"], "role": row["role"]},
        rows=roster(),
        announcement=row["notice"] or None,
    )
