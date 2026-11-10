"""Seed the challenge database from seed.sql + the FLAG env.

Interpolates ``__FLAG__`` into seed.sql and runs it against the SQLite
database on the /var/lib/app tmpfs. Runs on EVERY container start; seed.sql
must be idempotent by contract (CREATE TABLE IF NOT EXISTS + upsert) so a
re-run is safe. The flag enters the DB only through this path — it never
lives in the image.
"""
import os
import sqlite3

DB_PATH = "/var/lib/app/app.db"


def main() -> None:
    flag = os.environ.get("FLAG") or "flag{local_verify}"
    with open("/app/seed.sql", encoding="utf-8") as fh:
        sql = fh.read().replace("__FLAG__", flag)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
