"""
models/registration.py - Registration Model
AICTE Activity & Points Management System

OOP class for managing event registrations, attendance tracking,
and points management.
"""

import mysql.connector
from config import MYSQL_CONFIG


class Registration:
    """Represents a student's registration for an event."""

    def __init__(self, id=None, student_id=None, event_id=None,
                 registered_at=None, attended=False, points_awarded=0,
                 attendance_marked_at=None):
        self.id = id
        self.student_id = student_id
        self.event_id = event_id
        self.registered_at = registered_at
        self.attended = attended
        self.points_awarded = points_awarded
        self.attendance_marked_at = attendance_marked_at

    # =========================================================================
    # Database Connection Helper
    # =========================================================================
    @staticmethod
    def get_db():
        """Get a database connection."""
        return mysql.connector.connect(**MYSQL_CONFIG)

    # =========================================================================
    # Registration Operations
    # =========================================================================
    def save(self):
        """Register a student for an event."""
        db = self.get_db()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO registrations (student_id, event_id)
                VALUES (%s, %s)
            """
            cursor.execute(query, (self.student_id, self.event_id))
            db.commit()
            self.id = cursor.lastrowid
            return self.id
        except mysql.connector.IntegrityError:
            db.rollback()
            raise ValueError("Already registered for this event")
        finally:
            cursor.close()
            db.close()

    @classmethod
    def find(cls, student_id, event_id):
        """Find a registration by student and event."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM registrations
                WHERE student_id = %s AND event_id = %s
            """, (student_id, event_id))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def is_registered(cls, student_id, event_id):
        """Check if a student is already registered for an event."""
        return cls.find(student_id, event_id) is not None

    # =========================================================================
    # Attendance & Points
    # =========================================================================
    @classmethod
    def mark_attendance(cls, student_id, event_id, points):
        """Mark attendance and award points for a student."""
        db = cls.get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE registrations
                SET attended = 1, points_awarded = %s,
                    attendance_marked_at = CURRENT_TIMESTAMP
                WHERE student_id = %s AND event_id = %s
            """, (points, student_id, event_id))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    @classmethod
    def unmark_attendance(cls, student_id, event_id):
        """Remove attendance mark and revoke points."""
        db = cls.get_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                UPDATE registrations
                SET attended = 0, points_awarded = 0, attendance_marked_at = NULL
                WHERE student_id = %s AND event_id = %s
            """, (student_id, event_id))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    @classmethod
    def mark_attendance_bulk(cls, event_id, student_ids, points):
        """Mark attendance for multiple students at once."""
        db = cls.get_db()
        cursor = db.cursor()
        try:
            for student_id in student_ids:
                cursor.execute("""
                    UPDATE registrations
                    SET attended = 1, points_awarded = %s,
                        attendance_marked_at = CURRENT_TIMESTAMP
                    WHERE student_id = %s AND event_id = %s
                """, (points, student_id, event_id))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    @classmethod
    def mark_attendance_by_token(cls, student_id, qr_token):
        """Mark attendance using QR token. Returns (success, message)."""
        from models.event import Event
        event = Event.find_by_token(qr_token)
        if not event:
            return False, "Invalid QR code"
        if event.status != 'approved':
            return False, "This event is not active"

        # Check if student is registered
        reg = cls.find(student_id, event.id)
        if not reg:
            return False, "You are not registered for this event"
        if reg.attended:
            return False, "Attendance already marked"

        # Mark attendance
        cls.mark_attendance(student_id, event.id, event.points)
        return True, f"Attendance marked! You earned {event.points} points for '{event.title}'"

    # =========================================================================
    # Statistics
    # =========================================================================
    @classmethod
    def get_event_stats(cls, event_id):
        """Get registration and attendance statistics for an event."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_registered,
                    SUM(attended) as total_attended
                FROM registrations
                WHERE event_id = %s
            """, (event_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_system_stats(cls):
        """Get overall system statistics."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            stats = {}
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
            stats['total_students'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'club'")
            stats['total_clubs'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM events")
            stats['total_events'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM events WHERE status = 'approved'")
            stats['approved_events'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM events WHERE status = 'pending'")
            stats['pending_events'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM registrations")
            stats['total_registrations'] = cursor.fetchone()['count']

            cursor.execute("SELECT COALESCE(SUM(points_awarded), 0) as total FROM registrations WHERE attended = 1")
            stats['total_points_awarded'] = cursor.fetchone()['total']

            return stats
        finally:
            cursor.close()
            db.close()
