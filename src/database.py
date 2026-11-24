
import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "saip_local.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")

    return conn


def init_db():

    with get_connection() as conn:

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                must_change_password INTEGER DEFAULT 1,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_names_json TEXT NOT NULL,
                records_json TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)


def save_dataset(
    name,
    original_filename,
    row_count,
    column_names,
    records,
    metrics,
    username
):

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO datasets (
                name,
                original_filename,
                row_count,
                column_names_json,
                records_json,
                metrics_json,
                created_by,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            original_filename,
            row_count,
            json.dumps(column_names, ensure_ascii=False),
            json.dumps(records, ensure_ascii=False, default=str),
            json.dumps(metrics, ensure_ascii=False, default=str),
            username,
            now
        ))

        return cursor.lastrowid


def list_datasets():

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                id,
                name,
                original_filename,
                row_count,
                created_by,
                created_at
            FROM datasets
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


def get_dataset(dataset_id):

    with get_connection() as conn:

        row = conn.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,)
        ).fetchone()

    if not row:
        return None

    item = dict(row)

    item["records"] = json.loads(item.pop("records_json"))
    item["metrics"] = json.loads(item.pop("metrics_json"))
    item["column_names"] = json.loads(
        item.pop("column_names_json")
    )

    return item
