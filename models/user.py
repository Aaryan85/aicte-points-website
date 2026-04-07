"""
models/user.py - User Model
AICTE Activity & Points Management System

OOP class for managing users (students, clubs, admins).
Handles CRUD operations, password hashing, and authentication.
"""

import bcrypt
import mysql.connector
from config import MYSQL_CONFIG


class User:
    """Represents a user in the system (student, club, or admin)."""

    def __init__(self, id=None, username=None, email=None, password_hash=None,
                 role='student', full_name=None, department=None,
                 roll_number=None, club_name=None, club_description=None,
                 created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.department = department
        self.roll_number = roll_number
        self.club_name = club_name
        self.club_description = club_description
        self.created_at = created_at

    # =========================================================================
    # Database Connection Helper
    # =========================================================================
    @staticmethod
    def get_db():
        """Get a database connection from the pool."""
        return mysql.connector.connect(**MYSQL_CONFIG)

    # =========================================================================
    # Password Hashing
    # =========================================================================
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    # =========================================================================
    # CRUD Operations
    # =========================================================================
    def save(self):
        """Insert a new user into the database. Returns the new user ID."""
        db = self.get_db()
        cursor = db.cursor()
        try:
            query = """
                INSERT INTO users (username, email, password_hash, role, full_name,
                                   department, roll_number, club_name, club_description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                self.username, self.email, self.password_hash, self.role,
                self.full_name, self.department, self.roll_number,
                self.club_name, self.club_description
            ))
            db.commit()
            self.id = cursor.lastrowid
            return self.id
        except mysql.connector.IntegrityError as e:
            db.rollback()
            # Determine which field caused the duplicate
            if 'username' in str(e):
                raise ValueError("Username already exists")
            elif 'email' in str(e):
                raise ValueError("Email already exists")
            raise ValueError("User already exists")
        finally:
            cursor.close()
            db.close()

    @classmethod
    def find_by_id(cls, user_id):
        """Find a user by their ID."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def find_by_username(cls, username):
        """Find a user by username."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def find_by_email(cls, email):
        """Find a user by email."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            if row:
                return cls(**row)
            return None
        finally:
            cursor.close()
            db.close()

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate a user with username and password. Returns User or None."""
        user = cls.find_by_username(username)
        if user and cls.verify_password(password, user.password_hash):
            return user
        return None

    @classmethod
    def get_all_by_role(cls, role):
        """Get all users with a specific role."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE role = %s ORDER BY created_at DESC",
                (role,)
            )
            return [cls(**row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_all(cls):
        """Get all users."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users ORDER BY role, created_at DESC")
            return [cls(**row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            db.close()

    # =========================================================================
    # Student-Specific Methods
    # =========================================================================
    def get_total_points(self):
        """Get total AICTE points for a student."""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(points_awarded), 0) as total
                FROM registrations WHERE student_id = %s AND attended = 1
            """, (self.id,))
            result = cursor.fetchone()
            return result['total'] if result else 0
        finally:
            cursor.close()
            db.close()

    def get_category_points(self):
        """Get points broken down by category for a student."""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.category, COALESCE(SUM(r.points_awarded), 0) as points
                FROM registrations r
                JOIN events e ON r.event_id = e.id
                WHERE r.student_id = %s AND r.attended = 1
                GROUP BY e.category
            """, (self.id,))
            return {row['category']: row['points'] for row in cursor.fetchall()}
        finally:
            cursor.close()
            db.close()

    def get_event_history(self):
        """Get complete event participation history for a student."""
        db = self.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.id, e.title, e.category, e.event_date, e.venue, e.points,
                       r.attended, r.points_awarded, r.registered_at,
                       u.club_name
                FROM registrations r
                JOIN events e ON r.event_id = e.id
                JOIN users u ON e.club_id = u.id
                WHERE r.student_id = %s
                ORDER BY e.event_date DESC
            """, (self.id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_leaderboard(cls, limit=20):
        """Get top students by AICTE points."""
        db = cls.get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.id, u.full_name, u.department, u.roll_number,
                       COALESCE(SUM(r.points_awarded), 0) as total_points,
                       COUNT(CASE WHEN r.attended = 1 THEN 1 END) as events_attended
                FROM users u
                LEFT JOIN registrations r ON u.id = r.student_id AND r.attended = 1
                WHERE u.role = 'student'
                GROUP BY u.id, u.full_name, u.department, u.roll_number
                ORDER BY total_points DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        finally:
            cursor.close()
            db.close()

    def to_dict(self):
        """Convert user object to dictionary (excludes password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'department': self.department,
            'roll_number': self.roll_number,
            'club_name': self.club_name,
            'created_at': str(self.created_at) if self.created_at else None
        }
