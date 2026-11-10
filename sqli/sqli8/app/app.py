"""TransferOps Console - internal report console for the transfer fleet.

Deliberately vulnerable for the course lab:
 * the report writer takes the table name straight from the request and the
   filter straight from the query string, concatenated into SQL;
 * reports are written with INTO OUTFILE into /data/public/reports, which
   the app also serves to anyone at /reports/<file>.
The console itself only renders the three fleet tables.
"""
import os

import pymysql
from flask import Flask, render_template, request, send_from_directory

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = "/data/public/reports"
KNOWN_TABLES = ("transfers", "routes", "queues")

app = Flask(__name__)


def db():
    return pymysql.connect(
        host="127.0.0.1", user="app", password="apppass",
        database="appdb", autocommit=True,
    )


def static_img(*candidates):
    """First existing optional image (svg first), or None for the fallback."""
    for c in candidates:
        if os.path.exists(os.path.join(HERE, "static", "img", c)):
            return "/static/img/" + c
    return None


def table_rows(table):
    try:
        with db() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table} ORDER BY id LIMIT 20")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            return cols, [list(r) for r in rows]
    except pymysql.MySQLError:
        return [], []


def page(report=None):
    tables = {t: table_rows(t) for t in KNOWN_TABLES}
    return render_template(
        "index.html",
        name="TransferOps Console",
        tagline="Fleet transfers at a glance - export a report when you need it",
        tables=tables,
        report=report,
        logo=static_img("logo.svg", "logo.png"),
        hero=static_img("hero.svg", "hero.png", "hero.jpg", "hero.webp"),
    )


@app.route("/")
def index():
    return page()


@app.route("/report", methods=["GET"])
@app.route("/report/<table>", methods=["GET"])
def report(table=""):
    table = (table or request.args.get("table", "")).strip() or "transfers"
    flt = request.args.get("filter", "1=1").strip() or "1=1"
    fname = table + ".csv"
    target = os.path.join(REPORT_DIR, fname)
    # INTO OUTFILE refuses to overwrite an existing file - regenerate by
    # removing the previous export first.
    if os.path.exists(target):
        try:
            os.remove(target)
        except OSError:
            pass
    try:
        with db() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {table} WHERE {flt} "
                f"INTO OUTFILE '/data/public/reports/{fname}'"
            )
            rows = cur.rowcount
        size = os.path.getsize(target)
        result = {"ok": True, "error": None, "file": fname,
                  "rows": rows, "bytes": size}
    except pymysql.MySQLError as e:
        result = {"ok": False, "error": str(e), "file": fname,
                  "rows": 0, "bytes": 0}
    return page(result)


@app.route("/reports/<path:fname>")
def get_report(fname):
    return send_from_directory(REPORT_DIR, fname)
