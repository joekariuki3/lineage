from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.family.services import FamilyService

from .services import LinkService

link_bp = Blueprint("link", __name__)


@link_bp.route("/create_link", methods=["POST"])
@login_required
def create_link():
    family_id = request.form.get("family_id")
    if not family_id:
        flash("Family id is required", "info")
        return redirect(url_for("user.user_profile"))

    family_id = int(family_id)

    family_service = FamilyService()
    data, status = family_service.get_family_by_id(
        family_id=family_id, user_id=current_user.user_id
    )
    family, message, category = (
        data.get("data"),
        data.get("message"),
        data.get("category"),
    )
    if status != 200:
        flash(message, category)
        return redirect(url_for("user.user_profile"))

    link_service = LinkService()
    data, status = link_service.create_link(family)
    message, category = data.get("message"), data.get("category")
    flash(message, category)
    return redirect(url_for("user.user_profile"))


@link_bp.route("/delete_link", methods=["POST"])
@login_required
def delete_link():
    link_id = request.form.get("link_id")
    family_id = request.form.get("family_id")
    if not link_id:
        flash("Link id is required", "info")
        return redirect(url_for("user.user_profile"))
    elif not family_id:
        flash("Family id is required", "info")
        return redirect(url_for("user.user_profile"))

    link_id = int(link_id)
    family_id = int(family_id)

    link_service = LinkService()
    data, _ = link_service.delete_link(
        link_id=link_id, family_id=family_id, user_id=current_user.user_id
    )
    message, category = data.get("message"), data.get("category")

    flash(message, category)
    return redirect(url_for("user.user_profile"))
