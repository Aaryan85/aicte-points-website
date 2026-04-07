"""
routes/auth.py - Authentication Routes
AICTE Activity & Points Management System

Handles login, signup, and logout for all user roles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from utils.validators import validate_signup_data, validate_email, sanitize_input

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login for all roles."""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect_to_dashboard()

    if request.method == 'POST':
        username = sanitize_input(request.form.get('username'))
        password = request.form.get('password', '')

        # Validate inputs
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')

        # Authenticate user
        user = User.authenticate(username, password)
        if user:
            # Set session data
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            session.permanent = True

            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect_to_dashboard()
        else:
            flash('Invalid username or password', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration for students and clubs."""
    if 'user_id' in session:
        return redirect_to_dashboard()

    if request.method == 'POST':
        # Collect form data
        data = {
            'username': sanitize_input(request.form.get('username')),
            'email': sanitize_input(request.form.get('email')),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'full_name': sanitize_input(request.form.get('full_name')),
            'role': request.form.get('role', 'student'),
            'department': sanitize_input(request.form.get('department')),
            'roll_number': sanitize_input(request.form.get('roll_number')),
            'club_name': sanitize_input(request.form.get('club_name')),
            'club_description': sanitize_input(request.form.get('club_description')),
        }

        # Validate
        is_valid, errors = validate_signup_data(data)
        if not is_valid:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('auth/signup.html', data=data)

        # Create user
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                password_hash=User.hash_password(data['password']),
                role=data['role'],
                full_name=data['full_name'],
                department=data['department'] if data['role'] == 'student' else None,
                roll_number=data['roll_number'] if data['role'] == 'student' else None,
                club_name=data['club_name'] if data['role'] == 'club' else None,
                club_description=data['club_description'] if data['role'] == 'club' else None,
            )
            user.save()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/signup.html', data=data)
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
            return render_template('auth/signup.html', data=data)

    return render_template('auth/signup.html', data={})


@auth_bp.route('/logout')
def logout():
    """Clear session and log out user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


def redirect_to_dashboard():
    """Redirect user to their role-specific dashboard."""
    role = session.get('role')
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    elif role == 'club':
        return redirect(url_for('club.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))
