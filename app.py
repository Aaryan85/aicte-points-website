"""
app.py - Main Flask Application
AICTE Activity & Points Management System

Entry point for the application. Registers blueprints, configures
sessions, and defines error handlers.
"""

from flask import Flask, render_template, session, redirect, url_for
from config import SECRET_KEY, PERMANENT_SESSION_LIFETIME

# =============================================================================
# Create Flask Application
# =============================================================================
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = PERMANENT_SESSION_LIFETIME

# =============================================================================
# Register Blueprints
# =============================================================================
from routes.auth import auth_bp
from routes.student import student_bp
from routes.club import club_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(club_bp)
app.register_blueprint(admin_bp)


# =============================================================================
# Landing Page
# =============================================================================
@app.route('/')
def index():
    """Landing page — redirect to dashboard if logged in."""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'club':
            return redirect(url_for('club.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html')


# =============================================================================
# Error Handlers
# =============================================================================
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Custom 500 page."""
    return render_template('errors/500.html'), 500


# =============================================================================
# Context Processor — inject variables into all templates
# =============================================================================
@app.context_processor
def inject_globals():
    """Make session data available in all templates."""
    return {
        'current_user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'full_name': session.get('full_name'),
        },
        'is_logged_in': 'user_id' in session
    }


# =============================================================================
# Run Application
# =============================================================================
if __name__ == '__main__':
    # Ensure static subdirectories exist
    import os
    for d in ['static/qrcodes', 'static/certificates', 'static/reports']:
        os.makedirs(d, exist_ok=True)

    print("=" * 60)
    print("  AICTE Activity & Points Management System")
    print("  Running on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
