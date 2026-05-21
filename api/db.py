import os
import sqlite3
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latency.db")
TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
USE_TURSO = bool(TURSO_URL and TURSO_TOKEN)

_lock = threading.Lock()
_client = None

if USE_TURSO:
    from libsql_client import create_client_sync
    # libsql:// makes libsql-client pick the WebSocket transport, which the
    # newer Turso edges (AWS regions) reject. Force the HTTP transport.
    _url = TURSO_URL
    if _url.startswith("libsql://"):
        _url = "https://" + _url[len("libsql://"):]
    elif _url.startswith("ws://"):
        _url = "http://" + _url[len("ws://"):]
    elif _url.startswith("wss://"):
        _url = "https://" + _url[len("wss://"):]
    _client = create_client_sync(_url, auth_token=TURSO_TOKEN)


def _execute(sql: str, params: tuple = ()):
    """Run a single statement and return rows as a list of tuples."""
    if USE_TURSO:
        result = _client.execute(sql, list(params))
        return [tuple(row) for row in result.rows]
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        return rows
    finally:
        conn.close()


def init_db() -> None:
    with _lock:
        _execute(
            """
            CREATE TABLE IF NOT EXISTS TIME (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                site TEXT NOT NULL,
                time INTEGER NOT NULL
            )
            """
        )


def insert_time(type_: str, location: str, site: str, time_ms: int) -> None:
    with _lock:
        _execute(
            "INSERT INTO TIME (type, location, site, time) VALUES (?, ?, ?, ?)",
            (type_, location, site, int(time_ms)),
        )
