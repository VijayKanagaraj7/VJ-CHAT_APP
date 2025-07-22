import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from auth_models import db, User
from auth_forms import LoginForm, RegistrationForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Check if user entered email or username
        username_or_email = form.username.data.strip() if form.username.data else ""
        password = form.password.data
        
        # Try to find user by username first, then by email
        user = User.query.filter_by(username=username_or_email).first()
        if not user:
            user = User.query.filter_by(email=username_or_email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Log the user in
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            logging.info(f"User {user.username} logged in successfully")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('chat.index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'error')
            logging.warning(f"Failed login attempt for: {username_or_email}")
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User()
            user.username = form.username.data.strip() if form.username.data else ""
            user.email = form.email.data.strip().lower() if form.email.data else ""
            user.first_name = form.first_name.data.strip() if form.first_name.data else None
            user.last_name = form.last_name.data.strip() if form.last_name.data else None
            user.set_password(form.password.data)
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            # Log the user in automatically
            login_user(user)
            user.update_last_login()
            
            flash(f'Account created successfully! Welcome to VIJAY\'S CHAT APP, {user.get_full_name()}!', 'success')
            logging.info(f"New user registered: {user.username} ({user.email})")
            
            return redirect(url_for('chat.index'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred while creating your account. Username or email may already exist.', 'error')
            logging.error(f"Database integrity error during registration for {form.username.data}")
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'error')
            logging.error(f"Registration error: {e}")
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    username = current_user.username
    logout_user()
    flash('You have been logged out successfully.', 'info')
    logging.info(f"User {username} logged out")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileForm(current_user.email)
    
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data.strip() if form.first_name.data else None
            current_user.last_name = form.last_name.data.strip() if form.last_name.data else None
            current_user.email = form.email.data.strip().lower() if form.email.data else ""
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            logging.info(f"Profile updated for user: {current_user.username}")
            
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please choose a different email.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
            logging.error(f"Profile update error: {e}")
    
    # Pre-populate form with current user data
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/users')
@login_required
def users():
    """Display all users (admin functionality)"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users)