from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from extensions import bcrypt, db, limiter, oauth
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or len(name) > 100 or not email or len(email) > 120 or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        # Auto-login after registration
        login_user(user)
        flash(f'Welcome, {user.name}! Your account has been created.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() if email else None
        if user and user.password and password and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('home'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/auth/google/login')
@limiter.limit('10 per minute')
def google_login():
    if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
        flash('Google sign-in is not configured yet.', 'danger')
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth.route('/auth/google/callback')
@limiter.limit('10 per minute')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            userinfo = oauth.google.userinfo(token=token)

        email = (userinfo.get('email') or '').strip().lower()
        if not email or not userinfo.get('email_verified', False):
            flash('Google sign-in requires a verified email address.', 'danger')
            return redirect(url_for('auth.login'))

        name = (userinfo.get('name') or email.split('@')[0]).strip()[:100]
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, password='', is_verified=True)
            db.session.add(user)
            db.session.commit()
        elif not user.is_verified:
            user.is_verified = True
            db.session.commit()

        login_user(user)
        flash(f'Welcome, {user.name}!', 'success')
        return redirect(url_for('home'))
    except (OAuthError, SQLAlchemyError):
        db.session.rollback()
        flash('Google sign-in failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))