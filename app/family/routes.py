from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from .forms import CreateFamilyForm
from app.member.forms import MemberForm
from app.auth.services import AuthService
from .services import FamilyService
from app.member.services import MemberService

family_bp = Blueprint("family", __name__)


@family_bp.route("/family")
@family_bp.route("/family/<family_id>")
@login_required
def index(family_id=0):
    family_service = FamilyService()
    families = []
    if family_id != 0:
        AuthService.set_current_family_id(family_id)
        current_family_id = family_id
        if current_family_id:
            data, status = family_service.get_family_by_id(
                current_family_id, current_user.user_id
            )
            family, message, category = (
                data.get("data"),
                data.get("message"),
                data.get("category"),
            )
            if status != 200:
                flash(message, category)
            else:
                families = [family]
    elif current_user.is_authenticated:
        data, status = family_service.get_user_families(current_user.user_id)
        families, message, category = (
            data.get("data"),
            data.get("message"),
            data.get("category"),
        )
        if status != 200:
            flash(message, category)

    return render_template("family.html", families=families)


@family_bp.route("/create-family", methods=["GET", "POST"])
@login_required
def create_family():
    family_form = CreateFamilyForm()
    member_form = MemberForm()

    if family_form.validate_on_submit() and member_form.validate_on_submit():
        family_service = FamilyService()
        response = family_service.create_family(
            family_form.name.data, current_user.user_id
        )
        family_data, family_status_code = response
        family_message, family_category = (
            family_data.get("message"),
            family_data.get("category"),
        )
        if family_status_code != 201:
            flash(family_message, family_category)
            return redirect(url_for("family.index"))

        family = family_data.get("data")

        root_member_data = {
            "first_name": member_form.data.get("first_name"),
            "last_name": member_form.data.get("last_name"),
            "birthdate": member_form.data.get("birthdate"),
            "gender": member_form.data.get("gender"),
            "family_id": family.family_id,
            "alive": bool(member_form.data.get("alive")),
            "deathdate": member_form.data.get("deathdate"),
            "root": True,
        }

        member_service = MemberService()
        response = member_service.create_root_member(**root_member_data)
        member_data, member_status_code = response
        member_message, member_category = (
            member_data.get("message"),
            member_data.get("category"),
        )

        if family_status_code == 201 and member_status_code == 201:
            flash(family_message, family_category)
        flash(member_message, member_category)

        return redirect(url_for("family.index"))

    return render_template(
        "create_family.html",
        title="Create Family",
        form=family_form,
        memberForm=member_form,
    )


@family_bp.route("/family/delete/<family_id>", methods=["POST"])
@login_required
def delete_family(family_id):
    family_service = FamilyService()
    is_family_owner = family_service.family_belongs_to_user(
        family_id=int(family_id), user_id=current_user.user_id
    )
    if not is_family_owner:
        flash("You are not allowed to delete this family", "info")
        return redirect(url_for("user.user_profile"))

    data, _ = family_service.delete_family(family_id=family_id)
    message, category = data.get("message"), data.get("category")

    flash(message, category)
    return redirect(url_for("user.user_profile"))
