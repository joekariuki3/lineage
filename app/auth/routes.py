from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from . import bp
from .forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from .services import AuthService
from config import Config
from app.models import User
from app.user.services import saveUser
from app.extensions import db
from app.services.email_service import send_password_reset_email

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        status, message = saveUser(name=form.name.data, email=form.email.data, password=form.password.data)
        # sendEmailVerificationLink(user)
        if status == 201:
            flash(message[0], message[1])
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

# login user
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.authenticate(form.email.data, form.password.data)
        if not user:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:# if there is a query string in the url requires login 1st then go to the next_page
            next_page = url_for('family.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)

# login a guest user
@bp.route('/guest')
def guest():
    guest_name = Config.GUEST_NAME
    guest_email = Config.GUEST_EMAIL
    guest_password = Config.GUEST_PASSWORD
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))
    user = AuthService.authenticate(email=guest_email, password=guest_password)
    if not user:
        # create guest user
        if guest_name is None or guest_email is None or guest_password is None:
            flash("Guest name, email and password are required. Contact admin", 'danger')
            return redirect(url_for('auth.login'))
        user = User(name=guest_name, email=guest_email)
        user.set_password(guest_password)
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('family.index'))

# logout user
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# reset password
@bp.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('family.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


# reset password from email link
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
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title="New password", form=form)
