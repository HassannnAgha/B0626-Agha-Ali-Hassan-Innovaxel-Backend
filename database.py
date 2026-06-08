import sqlite3

DB_NAME = "events.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets you access columns by name like a dict
    conn.execute("PRAGMA journal_mode=WAL")  # allows concurrent reads/writes safely
    conn.execute("PRAGMA foreign_keys = ON")  # enforces foreign key relationships
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        total_seats INTEGER NOT NULL,
        available_seats INTEGER NOT NULL,
        event_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            registered_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (event_id) REFERENCES events(id),
            UNIQUE(event_id, user_name)
        )
    """)

    conn.commit()
    conn.close()