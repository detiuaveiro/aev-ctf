"""Guestbook - sign the book, leave a note.

Deliberately vulnerable for the course lab: the note insert builds its
statement by concatenating the name straight from the form.
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


def recent_notes():
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, message, signed_at FROM guestbook "
                "ORDER BY id DESC LIMIT 10"
            )
            return cur.fetchall()
    finally:
        conn.close()


def page(notes, error=None):
    return render_template(
        "index.html",
        name="Guestbook",
        tagline="Leave a note for the next shift",
        notes=notes,
        error=error,
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        nm = request.form.get("name", "")
        msg = request.form.get("message", "")
        conn = db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO guestbook (name, message) "
                    f"VALUES ('{nm}', '{msg}')"
                )
            conn.commit()
        except pymysql.Error:
            error = "The book was a bit ruffled - your note was not saved."
        finally:
            conn.close()
    return page(recent_notes(), error=error)
