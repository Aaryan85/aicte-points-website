"""
routes/club.py - Club Routes
AICTE Activity & Points Management System

Handles club dashboard, event CRUD, attendee management,
and QR code generation.
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session
)
from functools import wraps
from models.user import User
from models.event import Event
from models.registration import Registration
from utils.validators import validate_event_data, sanitize_input
from utils.qr_generator import generate_event_qr, get_qr_path

club_bp = Blueprint('club', __name__, url_prefix='/club')


# =============================================================================
# Authentication Decorator
# =============================================================================
def club_required(f):
    """Decorator to ensure user is logged in as a club."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'club':
            flash('Access denied. Club accounts only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Dashboard
# =============================================================================
@club_bp.route('/dashboard')
@club_required
def dashboard():
    """Club dashboard showing all events and statistics."""
    events = Event.get_club_events(session['user_id'])
    user = User.find_by_id(session['user_id'])

    # Calculate stats
    total_events = len(events)
    approved = sum(1 for e in events if e['status'] == 'approved')
    pending = sum(1 for e in events if e['status'] == 'pending')
    total_registrations = sum(e.get('registered_count', 0) for e in events)

    return render_template('club/dashboard.html',
        events=events,
        user=user,
        stats={
            'total_events': total_events,
            'approved': approved,
            'pending': pending,
            'total_registrations': total_registrations
        }
    )


# =============================================================================
# Create Event
# =============================================================================
@club_bp.route('/event/create', methods=['GET', 'POST'])
@club_required
def create_event():
    """Create a new event."""
    if request.method == 'POST':
        data = {
            'title': sanitize_input(request.form.get('title')),
            'description': sanitize_input(request.form.get('description')),
            'category': request.form.get('category'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'venue': sanitize_input(request.form.get('venue')),
            'points': request.form.get('points'),
            'max_participants': request.form.get('max_participants'),
        }

        # Validate
        is_valid, errors = validate_event_data(data)
        if not is_valid:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('club/create_event.html', data=data)

        try:
            event = Event(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                event_date=data['event_date'],
                event_time=data['event_time'],
                venue=data['venue'],
                points=int(data['points']),
                max_participants=int(data['max_participants']),
                club_id=session['user_id'],
                status='pending'
            )
            event_id = event.save()

            # Generate QR code
            qr_path = generate_event_qr(event_id, event.qr_token)

            flash('Event created! It will be visible after admin approval.', 'success')
            return redirect(url_for('club.dashboard'))
        except Exception as e:
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('club/create_event.html', data=data)

    return render_template('club/create_event.html', data={})


# =============================================================================
# Edit Event
# =============================================================================
@club_bp.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@club_required
def edit_event(event_id):
    """Edit an existing event."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    if request.method == 'POST':
        data = {
            'title': sanitize_input(request.form.get('title')),
            'description': sanitize_input(request.form.get('description')),
            'category': request.form.get('category'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'venue': sanitize_input(request.form.get('venue')),
            'points': request.form.get('points'),
            'max_participants': request.form.get('max_participants'),
        }

        # Validate
        is_valid, errors = validate_event_data(data)
        if not is_valid:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('club/edit_event.html', event=event, data=data)

        try:
            event.title = data['title']
            event.description = data['description']
            event.category = data['category']
            event.event_date = data['event_date']
            event.event_time = data['event_time']
            event.venue = data['venue']
            event.points = int(data['points'])
            event.max_participants = int(data['max_participants'])
            # Reset to pending if it was rejected
            if event.status == 'rejected':
                event.status = 'pending'
            event.update()

            flash('Event updated successfully!', 'success')
            return redirect(url_for('club.dashboard'))
        except Exception as e:
            flash(f'Error updating event: {str(e)}', 'error')
            return render_template('club/edit_event.html', event=event, data=data)

    return render_template('club/edit_event.html', event=event, data=event.to_dict())


# =============================================================================
# Delete Event
# =============================================================================
@club_bp.route('/event/delete/<int:event_id>', methods=['POST'])
@club_required
def delete_event(event_id):
    """Delete an event."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    try:
        event.delete()
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting event: {str(e)}', 'error')

    return redirect(url_for('club.dashboard'))


# =============================================================================
# View Event Attendees
# =============================================================================
@club_bp.route('/event/<int:event_id>/attendees')
@club_required
def event_attendees(event_id):
    """View registered students and manage attendance."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    students = event.get_registered_students()
    stats = Registration.get_event_stats(event_id)

    # Get QR code path
    qr_path = get_qr_path(event_id, event.qr_token)
    if not qr_path:
        # Generate if it doesn't exist
        qr_path = generate_event_qr(event_id, event.qr_token)

    return render_template('club/attendance.html',
        event=event,
        students=students,
        stats=stats,
        qr_path=qr_path
    )


# =============================================================================
# Mark Attendance
# =============================================================================
@club_bp.route('/event/<int:event_id>/mark-attendance', methods=['POST'])
@club_required
def mark_attendance(event_id):
    """Mark attendance for selected students."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    # Get list of student IDs from form checkboxes
    student_ids = request.form.getlist('student_ids')

    if not student_ids:
        flash('No students selected.', 'warning')
        return redirect(url_for('club.event_attendees', event_id=event_id))

    try:
        student_ids = [int(sid) for sid in student_ids]
        Registration.mark_attendance_bulk(event_id, student_ids, event.points)
        flash(f'Attendance marked for {len(student_ids)} student(s). Points awarded!', 'success')
    except Exception as e:
        flash(f'Error marking attendance: {str(e)}', 'error')

    return redirect(url_for('club.event_attendees', event_id=event_id))


# =============================================================================
# Toggle Individual Attendance
# =============================================================================
@club_bp.route('/event/<int:event_id>/toggle-attendance/<int:student_id>', methods=['POST'])
@club_required
def toggle_attendance(event_id, student_id):
    """Toggle attendance for a single student."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    reg = Registration.find(student_id, event_id)
    if not reg:
        flash('Registration not found.', 'error')
        return redirect(url_for('club.event_attendees', event_id=event_id))

    try:
        if reg.attended:
            Registration.unmark_attendance(student_id, event_id)
            flash('Attendance unmarked.', 'info')
        else:
            Registration.mark_attendance(student_id, event_id, event.points)
            flash('Attendance marked. Points awarded!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('club.event_attendees', event_id=event_id))
