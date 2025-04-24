from flask import render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_user, logout_user, current_user
from . import bp
from .forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from .services import AuthService
from config import Config
from app.models import User
from app.user.services import create_user, save_user, get_user, update_user, check_user_exists
from app.extensions import db
from app.services.email_service import send_password_reset_email

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = create_user(name=form.name.data, email=form.email.data, password=form.password.data)
        code, message, category = save_user(user)
        # sendEmailVerificationLink(user)
        if code == 201:
            flash(message, category)
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_exists = check_user_exists(form.email.data)
        if not user_exists:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        user = AuthService.authenticate(email=form.email.data, password=form.password.data)
        if isinstance(user, tuple): # if user is a tuple, it means they exist but password is wrong
            code, message, category = user
            if code == 403:
                flash(message, category)
                return redirect(url_for('auth.login'))

        next_page = request.args.get('next')
        if not next_page:# if there is a query string in the url requires login 1st then go to the next_page
            next_page = url_for('family.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/guest')
def guest():
    """Login as a guest user."""
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))

    guest_name, guest_email, guest_password = AuthService.get_guest_info()
    if not guest_name or not guest_email or not guest_password:
        flash("Guest name, email and password are required. Contact admin", 'danger')
        return redirect(url_for('auth.login'))

    guest_user_exists = check_user_exists(guest_email)
    if not guest_user_exists:
        guest_user = create_user(name=guest_name, email=guest_email, password=guest_password)
        code, message, category = save_user(guest_user)
        if code != 201:
            flash(message, category)
            return redirect(url_for('auth.login'))

    user = AuthService.authenticate(email=guest_email, password=guest_password)
    if isinstance(user, tuple): # if user is a tuple, it means authentication failed
        code, message, category = user
        if code == 403:
            flash(message, category)
            return redirect(url_for('auth.login'))
    return redirect(url_for('family.index'))

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = get_user(email=form.email.data)
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))

    user = User.verify_reset_password_token(app.config['SECRET_KEY'], token)
    if not user:
        flash('Link expired. Request for a new link', 'warning')
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        code, message, category = update_user(user, password=form.password.data)
        if code != 200:
            flash(message, category)
            return redirect(url_for('auth.reset_password', token=token))
        flash(message, category)
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title="New password", form=form)
