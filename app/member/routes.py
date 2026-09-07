
from flask import (
    Blueprint,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.models import Member
from app.relationship.services import RelationshipService
from app.utils.constants import RelationType

from .forms import MemberForm
from .services import MemberService

member_bp = Blueprint("member", __name__)


def retrieve_member(
    member_id: int, call_type: str | None = None
) -> Member | None | tuple[dict, int]:
    """
    Retrieve a member's details based on the provided member ID.

    This function interacts with the `MemberService` to fetch the details
    of the requested member. It checks whether the details are being retrieved
    for API calls or other purposes and handles responses accordingly.
    If the `call_type` is not specified or not 'api', any error messages
    or categories from the response are flashed for user notification.

    Parameters:
        member_id: int
            The unique identifier of the member to retrieve.
        call_type: Union[str, None], optional
            The type of call, which determines how the response is returned.
            Set to "api" for results formatted for API usage.

    Returns:
        Union[Member, None, Tuple[Dict, int]]:
            A Member object if the request is successful and not an API call.
            A tuple of data dictionary and status integer if `call_type` is "api".
            None if the request is unsuccessful and not an API call.
    """
    member_service = MemberService()
    data, status = member_service.get_member(member_id)
    if call_type == "api":
        return data, status
    member = data.get("data")
    return member


def retrieve_spouses(
    member_id: int, call_type: str | None = None
) -> list[Member] | None | tuple[dict, int]:
    """
    retrieves the spouses of a member based on the provided member ID. Depending on the provided
    call type or the success of the operation, returns either spouse data, a tuple containing
    additional details, or None.

    Parameters:
        member_id (int): The unique identifier of the member whose spouses need to be retrieved
        call_type (Union[str, None]): Specifies the context of the call, default is None. If "api",
            the function behaves differently and returns additional information.

    Returns:
        Union[List[Member], None, Tuple[Dict, int]]: A list of Member objects representing spouses if
            the operation is successful and `call_type` is not "api". Returns a tuple containing a
            dictionary (with details) and status code if `call_type` is "api". Returns None if no
            spouses were found or in case of an error.
    """
    member_service = MemberService()

    data, status = member_service.get_member_spouses(member_id)
    if call_type == "api":
        return data, status
    spouses = data.get("data")
    return spouses


def retrieve_children(
    member_id: int, call_type: str | None = None
) -> list[Member] | None | tuple[dict, int]:
    """
    Retrieve children for a given member ID with an optional API call type.

    This function interacts with the MemberService class to fetch children associated
    with a specific member ID. Depending on the call type and the status of the
    response, it either returns the data and status directly or processes the data to
    return the list of children. A flash message may be displayed if an error is
    encountered during the data retrieval process.

    Parameters:
    member_id: int
        The unique identifier of the parent member whose children are to be retrieved.
    call_type: Union[str, None], optional
        The type of call to be used during the retrieval process. This is particularly
        useful for API responses. Defaults to None.

    Returns:
    Union[List[Member], None, Tuple[Dict, int]]
        A list of children as Member objects if retrieval is successful without an API
        call type. If 'the api' call type is provided, a tuple containing the data and HTTP
        status code is returned. None is returned if there is an issue retrieving the
        children.
    """
    member_service = MemberService()

    data, status = member_service.get_member_children(member_id)
    if call_type == "api":
        return data, status
    children = data.get("data")
    return children


def create_relationship(
    member_id: int, new_member_id: int, relationship_type: RelationType
) -> tuple[dict, int]:
    """
    Creates a relationship between two members using the specified relationship type.

    This function interacts with the RelationshipService to establish a relationship
    between two specified members and returns the result along with the corresponding status code.

    Args:
        member_id (int): The unique identifier of the first member
        new_member_id (int): The unique identifier of the second member to establish the relationship with
        relationship_type (str): The type of relationship to create (e.g., spouse, child).

    Returns:
        Tuple[Dict, int]: A tuple consisting of a dictionary containing the result of the relationship creation
        and an integer representing the HTTP status code.
    """
    relationship_service = RelationshipService()
    return relationship_service.create_relationship(
        member_id, new_member_id, relationship_type
    )


@member_bp.route("/member/<member_id>/spouse", methods=["GET", "POST"])
@login_required
def add_spouse(member_id):
    form = MemberForm(add_relative_mode=RelationType.SPOUSE)
    member_service = MemberService()

    member1 = retrieve_member(member_id)
    if not member1:
        return redirect(url_for("family.index"))

    family_id = member1.family_id
    title = f"Adding spouse of {member1.first_name} {member1.last_name}"

    if form.validate_on_submit():
        spouse_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "birthdate": form.birthdate.data,
            "gender": form.gender.data,
            "family_id": family_id,
            "alive": bool(form.alive.data),
            "deathdate": form.deathdate.data,
        }
        data, status = member_service.create_member(**spouse_data)
        if status != 201:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("family.index"))

        new_member = data.get("data")

        data, status = create_relationship(
            member1.member_id, new_member.member_id, RelationType.SPOUSE
        )
        message, category = data.get("message"), data.get("category")
        if status != 201:
            flash(message, category)
            return redirect(url_for("family.index"))

        flash(
            f"{new_member.first_name} added as spouse to {member1.first_name} {member1.last_name}",
            "success",
        )
        return redirect(url_for("family.index"))

    return render_template(
        "add_member.html",
        title=title,
        form=form,
        families=current_user.families,
        member1=member1,
    )


@member_bp.route("/member/<member_id>/<spouse_id>/child", methods=["GET", "POST"])
@login_required
def add_child(member_id, spouse_id):
    form = MemberForm(add_relative_mode=RelationType.CHILD)
    father_id: int
    mother_id: int
    member_service: MemberService = MemberService()

    member1 = retrieve_member(member_id)
    if not member1:
        return redirect(url_for("family.index"))

    spouse = retrieve_member(spouse_id)
    if not spouse:
        return redirect(url_for("family.index"))

    if member1.gender == "Male":
        father_id = member1.member_id
        mother_id = spouse.member_id
    else:
        mother_id = member1.member_id
        father_id = spouse.member_id

    family_id = int(member1.family_id)

    if form.validate_on_submit():
        child_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "birthdate": form.birthdate.data,
            "gender": form.gender.data,
            "family_id": family_id,
            "alive": bool(form.alive.data),
            "deathdate": form.deathdate.data,
            "father": father_id,
            "mother": mother_id,
        }
        data, status = member_service.create_member(**child_data)

        if status != 201:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("family.index"))

        new_member = data.get("data")

        data, status = create_relationship(
            spouse.member_id, new_member.member_id, RelationType.CHILD
        )
        if status != 201:
            message, category = data.get("message"), data.get("category")
            flash(message, category)
            return redirect(url_for("family.index"))

        flash(
            f"{new_member.first_name} {new_member.last_name} added as child to {member1.first_name} {member1.last_name} and {spouse.first_name} {spouse.last_name}",
            "success",
        )
        return redirect(url_for("family.index"))
    return render_template(
        "add_member.html",
        title="Add child",
        form=form,
        families=current_user.families,
        member1=member1,
    )


@member_bp.route("/member/<member_id>", methods=["GET"])
@login_required
def member_profile(member_id):
    member_service = MemberService()

    member = retrieve_member(member_id)
    if not member:
        return redirect(url_for("family.index"))

    mother = retrieve_member(member.mother)
    father = retrieve_member(member.father)

    data, _ = member_service.get_member_siblings(member_id)
    siblings = data.get("data")
    # TODO: include step siblings

    children = retrieve_children(member_id)
    spouses = retrieve_spouses(member_id)

    return render_template(
        "member_profile.html",
        title=f"{member.first_name} information ",
        member=member,
        father=father,
        mother=mother,
        siblings=siblings,
        spouses=spouses,
        children=children,
    )


@member_bp.route("/update_member/<member_id>", methods=["GET", "POST"])
@login_required
def update_member(member_id):
    member_service = MemberService()
    form = MemberForm()

    member = retrieve_member(member_id)
    if not member:
        return redirect(url_for("family.index"))

    if form.validate_on_submit():
        data, status = member_service.update_member(
            member_id=member.member_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            deathdate=form.deathdate.data,
            alive=bool(form.alive.data),
        )
        message, category = data.get("message"), data.get("category")
        if status != 200:
            flash(message, category)
            return redirect(url_for("member.update_member", member_id=member.member_id))

        flash(message, category)
        return redirect(url_for("member.member_profile", member_id=member.member_id))

    return render_template(
        "update_member.html",
        title=f"Update {member.first_name} information ",
        form=form,
        member=member,
    )


@member_bp.route("/delete_member/<member_id>")
@login_required
def delete_member(member_id):
    member_service = MemberService()

    data, _ = member_service.delete_member(member_id)
    message, category = data.get("message"), data.get("category")
    flash(message, category)
    return redirect(url_for("family.index"))


# API call
@member_bp.route("/member/spouses", methods=["POST", "GET"])
@login_required
def get_spouse():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    member_id = int(data.get("member1_id"))
    spouses_list = []

    data, _ = retrieve_spouses(member_id=member_id, call_type="api")
    spouses = data.get("data")
    if spouses:
        for spouse in spouses:
            spouses_list.append(spouse.to_dict())

    if current_user.is_authenticated:
        login = {"authenticated": True}
    else:
        login = {"authenticated": False}
    response = make_response(jsonify(spouses_list, login), 200)
    return response


@member_bp.route("/member/children", methods=["POST", "GET"])
@login_required
def get_children():
    data = request.get_json()

    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    elif "spouse_id" not in data:
        return make_response(jsonify({"error": "Missing spouse_id"}), 400)

    member_id = int(data["member1_id"])
    spouse_id = int(data["spouse_id"])
    parent_ids = [member_id, spouse_id]

    data, status = retrieve_children(member_id=member_id, call_type="api")
    if status != 200:
        message, category = data.get("message"), data.get("category")
        return make_response(jsonify({category: message}), status)

    children = data.get("data")
    children_list = []

    if children:
        for child in children:
            if child.father in parent_ids and child.mother in parent_ids:
                children_list.append(child.to_dict())

    if current_user.is_authenticated:
        login = {"authenticated": True}
    else:
        login = {"authenticated": False}
    response = make_response(jsonify(children_list, login), 200)
    return response


@member_bp.route("/member/nuclear", methods=["POST", "GET"])
@login_required
def get_nuclear():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    member_id = int(data.get("member1_id"))
    parent_ids = [member_id]
    nuclear_family = {"spouses": [], "children": []}

    data, status = retrieve_spouses(member_id=member_id, call_type="api")
    if status != 200:
        message, category = data.get("message"), data.get("category")
        return make_response(jsonify({category: message}), status)
    spouses = data.get("data")

    if spouses:
        for spouse in spouses:
            parent_ids.append(spouse.member_id)
            nuclear_family["spouses"].append(spouse.to_dict())

    data, status = retrieve_children(member_id=member_id, call_type="api")
    if status != 200:
        message, category = data.get("message"), data.get("category")
        return make_response(jsonify({category: message}), status)

    children = data.get("data")

    if children:
        for child in children:
            if child.father in parent_ids and child.mother in parent_ids:
                nuclear_family["children"].append(child.to_dict())

    response = make_response(jsonify(nuclear_family), 200)
    return response
