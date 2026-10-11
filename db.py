"""SQLite storage for enquiries.

Schema (table ``enquiries``):

    id             INTEGER PRIMARY KEY AUTOINCREMENT
    created_at     TEXT     ISO-8601 UTC timestamp
    name           TEXT     customer name
    phone          TEXT     normalised as +91XXXXXXXXXX
    email          TEXT     optional
    property_type  TEXT     residential | agricultural | commercial | other
    location       TEXT     village / town
    monthly_bill   INTEGER  optional, rupees
    message        TEXT     optional requirements
    source         TEXT     page the form was submitted from
    fingerprint    TEXT     hash used to ignore accidental duplicate submissions
"""
import csv
import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone

import click
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS enquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    property_type TEXT NOT NULL,
    location TEXT NOT NULL,
    monthly_bill INTEGER,
    message TEXT,
    source TEXT,
    fingerprint TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_enquiries_fingerprint ON enquiries (fingerprint, created_at);
"""

FIELDS = ("name", "phone", "email", "property_type", "location", "monthly_bill", "message", "source")


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"], timeout=5)
        conn.row_factory = sqlite3.Row
        conn.executescript(SCHEMA)
        g.db = conn
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def fingerprint(data):
    raw = "|".join(str(data.get(k) or "").strip().lower() for k in ("name", "phone", "property_type", "location", "message"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_enquiry(data):
    """Store an enquiry. Returns (id, is_duplicate)."""
    conn = get_db()
    fp = fingerprint(data)
    now = datetime.now(timezone.utc)
    window = now - timedelta(minutes=current_app.config["DUPLICATE_WINDOW_MINUTES"])
    existing = conn.execute(
        "SELECT id FROM enquiries WHERE fingerprint = ? AND created_at >= ? ORDER BY id DESC LIMIT 1",
        (fp, window.isoformat(timespec="seconds")),
    ).fetchone()
    if existing:
        return existing["id"], True
    with conn:
        cur = conn.execute(
            f"INSERT INTO enquiries (created_at, {', '.join(FIELDS)}, fingerprint) "
            f"VALUES (?, {', '.join('?' for _ in FIELDS)}, ?)",
            (now.isoformat(timespec="seconds"), *(data.get(k) for k in FIELDS), fp),
        )
    return cur.lastrowid, False


def _csv_safe(value):
    """Stop spreadsheet apps from treating customer text as a formula."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """Create the enquiries table if it does not exist."""
        get_db()
        click.echo(f"Database ready at {app.config['DATABASE']}")

    @app.cli.command("list-enquiries")
    @click.option("--limit", default=20, show_default=True)
    def list_enquiries_command(limit):
        """Print the most recent enquiries (run on the server only)."""
        rows = get_db().execute("SELECT * FROM enquiries ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        if not rows:
            click.echo("No enquiries yet.")
        for r in rows:
            click.echo(
                f"#{r['id']} {r['created_at']} | {r['name']} | {r['phone']} | {r['property_type']} | "
                f"{r['location']} | bill: {r['monthly_bill'] or '-'}\n    {r['message'] or ''}"
            )

    @app.cli.command("export-enquiries")
    @click.argument("path", default="enquiries.csv")
    def export_enquiries_command(path):
        """Export all enquiries to a CSV file. Keep the file private."""
        rows = get_db().execute("SELECT * FROM enquiries ORDER BY id").fetchall()
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "created_at", *FIELDS])
            for r in rows:
                writer.writerow([r["id"], r["created_at"], *(_csv_safe(r[k]) for k in FIELDS)])
        click.echo(f"Exported {len(rows)} enquiries to {path}")
