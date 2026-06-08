import sqlite3
from database import get_connection


# ─── Events ───────────────────────────────────────────────

def create_event(name: str, total_seats: int, event_date: str, start_time: str, end_time: str):
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO events (name, total_seats, available_seats, event_date, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, total_seats, total_seats, event_date, start_time, end_time)
        )
        conn.commit()
        event = conn.execute(
            "SELECT * FROM events WHERE name = ?", (name,)
        ).fetchone()
        return dict(event)
    except sqlite3.IntegrityError:
        raise ValueError("Event name already exists")
    finally:
        conn.close()

def get_events(upcoming_only: bool = False, sort_by_date: bool = False):
    conn = get_connection()
    try:
        query = """
            SELECT 
                e.*,
                COUNT(CASE WHEN r.status = 'active' THEN 1 END) as total_registrations
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
        """
        if upcoming_only:
            query += " WHERE e.event_date > datetime('now')"

        query += " GROUP BY e.id"

        if sort_by_date:
            query += " ORDER BY e.event_date ASC"

        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_event_by_id(event_id: int):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT 
                e.*,
                COUNT(CASE WHEN r.status = 'active' THEN 1 END) as total_registrations
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            WHERE e.id = ?
            GROUP BY e.id
            """,
            (event_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ─── Registrations ─────────────────────────────────────────

def register_user(event_id: int, user_name: str):
    conn = get_connection()
    try:
        # check event exists first
        event = conn.execute(
            "SELECT * FROM events WHERE id = ?", (event_id,)
        ).fetchone()
        if not event:
            raise LookupError("Event not found")

        # atomic seat decrement — race condition fix
        cursor = conn.execute(
            """
            UPDATE events 
            SET available_seats = available_seats - 1
            WHERE id = ? AND available_seats > 0
            """,
            (event_id,)
        )

        if cursor.rowcount == 0:
            raise OverflowError("Event is full")

        # insert registration — UNIQUE constraint catches duplicate
        try:
            conn.execute(
                """
                INSERT INTO registrations (event_id, user_name)
                VALUES (?, ?)
                """,
                (event_id, user_name)
            )
        except sqlite3.IntegrityError:
            # user already registered — undo the seat decrement
            conn.execute(
                "UPDATE events SET available_seats = available_seats + 1 WHERE id = ?",
                (event_id,)
            )
            raise ValueError("User already registered for this event")

        conn.commit()

        reg = conn.execute(
            """
            SELECT * FROM registrations 
            WHERE event_id = ? AND user_name = ? AND status = 'active'
            """,
            (event_id, user_name)
        ).fetchone()
        return dict(reg)

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cancel_registration(registration_id: int, user_name: str):
    conn = get_connection()
    try:
        reg = conn.execute(
            """
            SELECT * FROM registrations 
            WHERE id = ? AND user_name = ? AND status = 'active'
            """,
            (registration_id, user_name)
        ).fetchone()

        if not reg:
            raise LookupError("Active registration not found")

        # cancel it
        conn.execute(
            "UPDATE registrations SET status = 'cancelled' WHERE id = ?",
            (registration_id,)
        )

        # give the seat back — both in one transaction
        conn.execute(
            "UPDATE events SET available_seats = available_seats + 1 WHERE id = ?",
            (reg["event_id"],)
        )

        conn.commit()
        return {"message": "Registration cancelled successfully"}

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()