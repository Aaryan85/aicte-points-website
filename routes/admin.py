"""
routes/admin.py - Admin Routes
AICTE Activity & Points Management System

Handles admin dashboard, event approval/rejection, and user management.
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session
)
from functools import wraps
from models.user import User
from models.event import Event
from models.registration import Registration

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# =============================================================================
# Authentication Decorator
# =============================================================================
def admin_required(f):
    """Decorator to ensure user is logged in as admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admin only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Dashboard
# =============================================================================
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with system overview and pending approvals."""
    pending_events = Event.get_pending_events()
    all_events = Event.get_all_events()
    stats = Registration.get_system_stats()
    leaderboard = User.get_leaderboard(limit=10)

    return render_template('admin/dashboard.html',
        pending_events=pending_events,
        all_events=all_events,
        stats=stats,
        leaderboard=leaderboard
    )


# =============================================================================
# Approve Event
# =============================================================================
@admin_bp.route('/event/<int:event_id>/approve', methods=['POST'])
@admin_required
def approve_event(event_id):
    """Approve a pending event."""
    try:
        success = Event.approve(event_id)
        if success:
            flash('Event approved and now visible to students!', 'success')
        else:
            flash('Event not found.', 'error')
    except Exception as e:
        flash(f'Error approving event: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))


# =============================================================================
# Reject Event
# =============================================================================
@admin_bp.route('/event/<int:event_id>/reject', methods=['POST'])
@admin_required
def reject_event(event_id):
    """Reject a pending event with a reason."""
    reason = request.form.get('reason', 'No reason provided')
    try:
        success = Event.reject(event_id, reason)
        if success:
            flash('Event rejected.', 'info')
        else:
            flash('Event not found.', 'error')
    except Exception as e:
        flash(f'Error rejecting event: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))


# =============================================================================
# View All Users
# =============================================================================
@admin_bp.route('/users')
@admin_required
def view_users():
    """View all registered users."""
    role_filter = request.args.get('role', 'all')
    if role_filter in ['student', 'club', 'admin']:
        users = User.get_all_by_role(role_filter)
    else:
        users = User.get_all()

    return render_template('admin/users.html',
        users=users,
        current_filter=role_filter
    )


# =============================================================================
# Leaderboard (Admin View)
# =============================================================================
@admin_bp.route('/leaderboard')
@admin_required
def leaderboard():
    """Full leaderboard view for admin."""
    rankings = User.get_leaderboard(limit=100)
    return render_template('student/leaderboard.html',
        rankings=rankings,
        current_user_id=None
    )
