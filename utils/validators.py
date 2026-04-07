"""
utils/validators.py - Input Validation Helpers
AICTE Activity & Points Management System

Provides regex-based validation for emails, passwords, and general input.
"""

import re


def validate_email(email):
    """
    Validate email format using regex.
    Returns True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    Requirements: at least 6 characters.
    Returns (is_valid, message).
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"


def validate_username(username):
    """
    Validate username format.
    Must be 3-80 characters, alphanumeric with underscores.
    """
    pattern = r'^[a-zA-Z0-9_]{3,80}$'
    if not re.match(pattern, username):
        return False, "Username must be 3-80 characters (letters, numbers, underscores only)"
    return True, "Username is valid"


def sanitize_input(text):
    """
    Basic input sanitization - strip whitespace and limit length.
    """
    if text is None:
        return ''
    return str(text).strip()[:500]


def validate_event_data(data):
    """
    Validate event creation/update data.
    Returns (is_valid, errors_dict).
    """
    errors = {}

    if not data.get('title', '').strip():
        errors['title'] = 'Event title is required'
    elif len(data['title']) > 200:
        errors['title'] = 'Title must be under 200 characters'

    if data.get('category') not in ['technical', 'cultural', 'social', 'sports']:
        errors['category'] = 'Invalid category'

    if not data.get('event_date'):
        errors['event_date'] = 'Event date is required'

    if not data.get('event_time'):
        errors['event_time'] = 'Event time is required'

    if not data.get('venue', '').strip():
        errors['venue'] = 'Venue is required'

    try:
        points = int(data.get('points', 0))
        if points < 1 or points > 20:
            errors['points'] = 'Points must be between 1 and 20'
    except (ValueError, TypeError):
        errors['points'] = 'Points must be a valid number'

    try:
        max_p = int(data.get('max_participants', 0))
        if max_p < 1:
            errors['max_participants'] = 'Max participants must be at least 1'
    except (ValueError, TypeError):
        errors['max_participants'] = 'Max participants must be a valid number'

    return len(errors) == 0, errors


def validate_signup_data(data):
    """
    Validate signup form data.
    Returns (is_valid, errors_dict).
    """
    errors = {}

    # Username validation
    valid, msg = validate_username(data.get('username', ''))
    if not valid:
        errors['username'] = msg

    # Email validation
    if not validate_email(data.get('email', '')):
        errors['email'] = 'Please enter a valid email address'

    # Password validation
    valid, msg = validate_password(data.get('password', ''))
    if not valid:
        errors['password'] = msg

    # Confirm password
    if data.get('password') != data.get('confirm_password'):
        errors['confirm_password'] = 'Passwords do not match'

    # Full name
    if not data.get('full_name', '').strip():
        errors['full_name'] = 'Full name is required'

    # Role-specific validation
    role = data.get('role', 'student')
    if role == 'student':
        if not data.get('department', '').strip():
            errors['department'] = 'Department is required'
        if not data.get('roll_number', '').strip():
            errors['roll_number'] = 'Roll number is required'
    elif role == 'club':
        if not data.get('club_name', '').strip():
            errors['club_name'] = 'Club name is required'

    return len(errors) == 0, errors
