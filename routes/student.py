"""
routes/student.py - Student Routes
AICTE Activity & Points Management System

Handles student dashboard, event browsing, registration,
QR attendance, leaderboard, and PDF report/certificate downloads.
"""

import os
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, send_file, jsonify
)
from functools import wraps
from models.user import User
from models.event import Event
from models.registration import Registration
from utils.pdf_generator import generate_report, generate_certificate
from config import MAX_AICTE_POINTS

student_bp = Blueprint('student', __name__, url_prefix='/student')


# =============================================================================
# Authentication Decorator
# =============================================================================
def student_required(f):
    """Decorator to ensure user is logged in as a student."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'student':
            flash('Access denied. Students only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Dashboard
# =============================================================================
@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Student dashboard with points summary and event history."""
    user = User.find_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    total_points = user.get_total_points()
    category_points = user.get_category_points()
    event_history = user.get_event_history()
    progress = min((total_points / MAX_AICTE_POINTS) * 100, 100)

    return render_template('student/dashboard.html',
        user=user,
        total_points=total_points,
        max_points=MAX_AICTE_POINTS,
        category_points=category_points,
        event_history=event_history,
        progress=progress
    )


# =============================================================================
# Browse Events
# =============================================================================
@student_bp.route('/events')
@student_required
def events():
    """Browse all approved events with category filtering."""
    category = request.args.get('category', 'all')
    all_events = Event.get_approved_events(category if category != 'all' else None)

    # Check which events the student is already registered for
    registered_event_ids = set()
    for event in all_events:
        if Registration.is_registered(session['user_id'], event['id']):
            registered_event_ids.add(event['id'])

    return render_template('student/events.html',
        events=all_events,
        registered_event_ids=registered_event_ids,
        current_category=category
    )


# =============================================================================
# Register for Event
# =============================================================================
@student_bp.route('/register/<int:event_id>', methods=['POST'])
@student_required
def register_event(event_id):
    """Register student for an event."""
    event = Event.find_by_id(event_id)

    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('student.events'))

    if event.status != 'approved':
        flash('This event is not available for registration.', 'error')
        return redirect(url_for('student.events'))

    # Check capacity
    if event.is_full():
        flash('Sorry, this event is full.', 'error')
        return redirect(url_for('student.events'))

    # Check for duplicate registration
    if Registration.is_registered(session['user_id'], event_id):
        flash('You are already registered for this event.', 'warning')
        return redirect(url_for('student.events'))

    # Register
    try:
        reg = Registration(student_id=session['user_id'], event_id=event_id)
        reg.save()
        flash(f'Successfully registered for "{event.title}"!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception:
        flash('An error occurred. Please try again.', 'error')

    return redirect(url_for('student.events'))


# =============================================================================
# QR Code Attendance
# =============================================================================
@student_bp.route('/attend/<token>')
@student_required
def attend_via_qr(token):
    """Mark attendance via QR code scan."""
    success, message = Registration.mark_attendance_by_token(
        session['user_id'], token
    )
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('student.dashboard'))


# =============================================================================
# Leaderboard
# =============================================================================
@student_bp.route('/leaderboard')
@student_required
def leaderboard():
    """Display student leaderboard by AICTE points."""
    rankings = User.get_leaderboard(limit=50)
    return render_template('student/leaderboard.html',
        rankings=rankings,
        current_user_id=session['user_id']
    )


# =============================================================================
# Download AICTE Points Report
# =============================================================================
@student_bp.route('/report')
@student_required
def download_report():
    """Generate and download AICTE points report PDF."""
    user = User.find_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('student.dashboard'))

    total_points = user.get_total_points()
    category_points = user.get_category_points()
    event_history = user.get_event_history()

    try:
        filepath = generate_report(user, total_points, category_points, event_history)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"AICTE_Report_{user.roll_number}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('student.dashboard'))


# =============================================================================
# Download Certificate
# =============================================================================
@student_bp.route('/certificate/<int:event_id>')
@student_required
def download_certificate(event_id):
    """Generate and download participation certificate."""
    user = User.find_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('student.dashboard'))

    # Check if student attended this event
    reg = Registration.find(session['user_id'], event_id)
    if not reg or not reg.attended:
        flash('Certificate is only available for events you have attended.', 'error')
        return redirect(url_for('student.dashboard'))

    event = Event.find_by_id(event_id)
    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('student.dashboard'))

    try:
        event_dict = event.to_dict()
        event_dict['event_date'] = event.event_date
        event_dict['venue'] = event.venue
        filepath = generate_certificate(user, event_dict)
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"Certificate_{event.title.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'Error generating certificate: {str(e)}', 'error')
        return redirect(url_for('student.dashboard'))
