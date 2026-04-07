"""
models/event.py - Event Model
AICTE Activity & Points Management System

OOP class for managing events with CRUD operations,
filtering, and participant tracking.
"""

import uuid
import mysql.connector
from config import MYSQL_CONFIG


class Event:
    """Represents an event in the system."""

    def __init__(self, id=None, title=None, description=None, category=None,
                 event_date=None, event_time=None, venue=None, points=0,
                 max_participants=0, club_id=None, status='pending',
                 qr_token=None, qr_code_path=None, rejection_reason=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.event_date = event_date
        self.event_time = event_time
        self.venue = venue
        self.points = points
        self.max_participants = max_participants
        self.club_id = club_id
        self.status = status
        self.qr_token = qr_token or str(uuid.uuid4().hex[:16])
        self.qr_code_path = qr_code_path
        self.rejection_reason = rejection_reason
        self.created_at = created_at
        self.updated_at = updated_at

    # =========================================================================
    # Database Connection Helper
    # =========================================================================
    @staticmethod
    def get_db():
        """Get a database connection."""
        return mysql.connector.connect(**MYSQL_CONFIG)

    # =========================================================================
    # CRUD Operations
    # =========================================================================
    def save(self):
        """Insert a new event into the database."""
        db = self.get_db()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO events (title, description, category, event_date,
                                    event_time, venue, points, max_participants,
                                    club_id, status, qr_token, qr_code_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                self.title, self.description, self.category, self.event_date,
                self.event_time, self.venue, self.points, self.max_participants,
                self.club_id, self.status, self.qr_token, self.qr_code_path
            ))
            db.commit()
            self.id = cursor.lastrowid
            return self.id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def update(self):
        """Update an existing event."""
        db = self.get_db()
        cursor = db.cursor()
        try:
            query = """
                UPDATE events SET title=%s, description=%s, category=%s,
                    event_date=%s, event_time=%s, venue=%s, points=%s,
                    max_participants=%s, status=%s
                WHERE id=%s AND club_id=%s
            """
            cursor.execute(query, (
                self.title, self.description, self.category, self.event_date,
                self.event_time, self.venue, self.points, self.max_participants,
                self.status, self.id, self.club_id
            ))
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    def delete(self):
        """Delete an event."""
        db = self.get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "DELETE FROM events WHERE id = %s AND club_id = %s",
                (self.id, self.club_id)
            )
            db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
            db.close()

    # =========================================================================
    # Query Methods
    # =========================================================================
    @classmethod
    def find_by_id(cls, event_id):
        """Find an event by ID."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def find_by_token(cls, token):
        """Find an event by its QR token."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM events WHERE qr_token = %s", (token,))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_approved_events(cls, category=None):
        """Get all approved events, optionally filtered by category."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            if category and category != 'all':
                cursor.execute("""
                    SELECT e.*, u.club_name,
                        (SELECT COUNT(*) FROM registrations WHERE event_id = e.id) as registered_count
                    FROM events e
                    JOIN users u ON e.club_id = u.id
                    WHERE e.status = 'approved' AND e.category = %s
                    ORDER BY e.event_date ASC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT e.*, u.club_name,
                        (SELECT COUNT(*) FROM registrations WHERE event_id = e.id) as registered_count
                    FROM events e
                    JOIN users u ON e.club_id = u.id
                    WHERE e.status = 'approved'
                    ORDER BY e.event_date ASC
                """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_club_events(cls, club_id):
        """Get all events for a specific club."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.*,
                    (SELECT COUNT(*) FROM registrations WHERE event_id = e.id) as registered_count
                FROM events e
                WHERE e.club_id = %s
                ORDER BY e.created_at DESC
            """, (club_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_pending_events(cls):
        """Get all pending events (for admin approval)."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.*, u.club_name
                FROM events e
                JOIN users u ON e.club_id = u.id
                WHERE e.status = 'pending'
                ORDER BY e.created_at ASC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_all_events(cls):
        """Get all events (for admin view)."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.*, u.club_name,
                    (SELECT COUNT(*) FROM registrations WHERE event_id = e.id) as registered_count
                FROM events e
                JOIN users u ON e.club_id = u.id
                ORDER BY e.created_at DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def approve(cls, event_id):
        """Approve an event."""
        db = cls.get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE events SET status = 'approved' WHERE id = %s",
                (event_id,)
            )
            db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            db.close()

    @classmethod
    def reject(cls, event_id, reason=''):
        """Reject an event with a reason."""
        db = cls.get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE events SET status = 'rejected', rejection_reason = %s WHERE id = %s",
                (reason, event_id)
            )
            db.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            db.close()

    def get_registered_students(self):
        """Get all students registered for this event."""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.id, u.full_name, u.email, u.department, u.roll_number,
                       r.registered_at, r.attended, r.points_awarded
                FROM registrations r
                JOIN users u ON r.student_id = u.id
                WHERE r.event_id = %s
                ORDER BY u.full_name
            """, (self.id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def get_participant_count(self):
        """Get current number of registered participants."""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT COUNT(*) as count FROM registrations WHERE event_id = %s",
                (self.id,)
            )
            result = cursor.fetchone()
            return result['count'] if result else 0
        finally:
            cursor.close()
            db.close()

    def is_full(self):
        """Check if event has reached max capacity."""
        return self.get_participant_count() >= self.max_participants

    def to_dict(self):
        """Convert event object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'event_date': str(self.event_date) if self.event_date else None,
            'event_time': str(self.event_time) if self.event_time else None,
            'venue': self.venue,
            'points': self.points,
            'max_participants': self.max_participants,
            'club_id': self.club_id,
            'status': self.status,
            'qr_token': self.qr_token
        }
