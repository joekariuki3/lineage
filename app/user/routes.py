from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user
from .forms import EditProfileForm
from .services import UserService
from app.services.email_service import sendEmailVerificationLink
from itsdangerous import URLSafeSerializer

user_bp = Blueprint("user", __name__)


@user_bp.route("/user/profile")
@login_required
def user_profile():
    url_root = request.url_root
    return render_template("profile.html", title="User_Profile", url_root=url_root)


@user_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    user_service = UserService()
    edit_profile_form = EditProfileForm()

    if edit_profile_form.validate_on_submit():
        data, status = user_service.update_user(
            current_user,
            name=edit_profile_form.name.data,
            email=edit_profile_form.email.data,
        )

        message, category = data.get("message"), data.get("category")
        if status != 200:
            flash(message, category)
            return render_template(
                "edit_profile.html", title="Edit Profile", form=edit_profile_form
            )

        flash(message, category)
        return redirect(url_for("user.user_profile"))

    edit_profile_form.name.data = current_user.name
    edit_profile_form.email.data = current_user.email
    return render_template(
        "edit_profile.html", title="Edit Profile", form=edit_profile_form
    )


@user_bp.route("/user/verify_email/<user_id>")
@login_required
def verify_email(user_id):
    user_service = UserService()

    data, status = user_service.get_user(user_id=user_id)
    if status != 200:
        message, category = data.get("message"), data.get("category")
        flash(message, category)
        return redirect(url_for("user.user_profile"))

    user = data.get("data")
    sendEmailVerificationLink(user)
    return redirect(url_for("user.user_profile"))


@user_bp.route("/verify_email/<token>")
def update_verify_email(token):
    user_service = UserService()

    auth_s = URLSafeSerializer(
        current_app.config["SECRET_KEY"], current_app.config["SALT"]
    )
    data = auth_s.loads(token)

    user_id = data["user_id"]

    if user_id:
        data, status = user_service.get_user(user_id=user_id)
        if status != 200:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("auth.login"))

        user = data.get("data")
        data, status = user_service.update_user(user, emailVerify=True)
        if status != 200:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("auth.login"))
        message, category = data.get("message"), data.get("category")
        flash(message, category)
    return redirect(url_for("auth.login"))
