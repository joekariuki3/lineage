from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import current_user, logout_user

from app.models import User
from app.services.email_service import send_password_reset_email
from app.user.services import UserService

from .forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordRequestForm
from .services import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    user_service = UserService()

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        data, status = user_service.create_user(
            name=form.name.data, email=form.email.data, password=form.password.data
        )
        # sendEmailVerificationLink(user)
        if status == 201:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("family.index"))

    form = LoginForm()
    if form.validate_on_submit():
        authenticate_service = AuthService()

        data, status = authenticate_service.authenticate(
            email=form.email.data, password=form.password.data
        )
        if status != 200:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("auth.login"))

        next_page = request.args.get("next")
        if not next_page:  # if there is a query string in the url requires login first, then go to the next_page
            next_page = url_for("family.index")
        return redirect(next_page)
    return render_template("auth/login.html", title="Login", form=form)


@auth_bp.route("/guest")
def guest():
    if current_user.is_authenticated:
        return redirect(url_for("family.index"))

    authenticate_service = AuthService()

    guest_name, guest_email, guest_password = authenticate_service.get_guest_info()
    if not guest_name or not guest_email or not guest_password:
        message = "Guest name, email and password are required. Contact admin"
        category = "danger"
        flash(message, category)
        return redirect(url_for("auth.login"))

    data, status = authenticate_service.authenticate(
        email=guest_email, password=guest_password
    )
    if status != 200:
        message, category = data.get("message"), data.get("category")
        flash(message, category)
        return redirect(url_for("auth.login"))
    return redirect(url_for("family.index"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth_bp.route("/reset_password_request", methods=["POST", "GET"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("family.index"))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user_service = UserService()

        data, _ = user_service.get_user(email=form.email.data)
        user = data.get("data")
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password", "info")
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html", title="Reset Password", form=form
    )


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("family.index"))

    user = User.verify_reset_password_token(app.config["SECRET_KEY"], token)
    if not user:
        flash("Link expired. Request for a new link", "warning")
        return redirect(url_for("auth.reset_password_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_service = UserService()

        data, status = user_service.update_user(user, password=form.password.data)
        if status != 200:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("auth.reset_password", token=token))

        message, category = data.get("message"), data.get("category")
        flash(message, category)
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", title="New password", form=form)
