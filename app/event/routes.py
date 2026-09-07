from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from .forms import AddEventForm
from .services import EventService

event_bp = Blueprint("event", __name__)


@event_bp.route("/event/", methods=["POST", "GET"])
@login_required
def add_event():
    families = [family for family in current_user.families]
    if len(families) < 1:
        flash("At least one family is required to add an event", "warning")
        return redirect(url_for("family.index"))

    form = AddEventForm()
    if form.validate_on_submit():
        event_service = EventService()

        data, status = event_service.create_event(
            event_date=form.date.data,
            event_name=form.name.data,
            family_id=int(request.form.get("family")),
            location=form.location.data,
            description=form.description.data,
        )

        event, message, category = (
            data.get("data"),
            data.get("message"),
            data.get("category"),
        )

        if status != 201:
            flash(message, category)
            return render_template("add_event.html", title="Add Event", form=form)

        flash(message, category)
        return redirect(url_for("event.get_events", family_id=event.family_id))
    return render_template(
        "add_event.html", title="Add Event", form=form, families=families
    )


@event_bp.route("/event/<family_id>")
@login_required
def get_events(family_id):
    event_service = EventService()

    data, _ = event_service.get_upcoming_events(family_id)
    upcoming_events, _, _ = (
        data.get("data", []),
        data.get("message"),
        data.get("category"),
    )

    data, _ = event_service.get_past_events(family_id)
    past_events, _, _ = data.get("data", []), data.get("message"), data.get("category")

    return render_template(
        "events.html", upcomingEvents=upcoming_events, pastEvents=past_events
    )


@event_bp.route("/delete/event/<event_id>", methods=["POST"])
@login_required
def delete_event(event_id):
    event_service = EventService()

    data, _ = event_service.delete_an_event(event_id)

    _, message, category = (
        data.get("data"),
        data.get("message"),
        data.get("category"),
    )

    flash(message, category)
    return redirect(
        url_for("event.get_events", family_id=session.get("current_family_id"))
    )


@event_bp.route("/edit/event/<event_id>", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event_service = EventService()

    data, status = event_service.get_event(event_id)
    retrieved_event, message, category = (
        data.get("data"),
        data.get("message"),
        data.get("category"),
    )
    if status != 200:
        flash(message, category)
        return redirect(
            url_for("event.get_events", family_id=session.get("current_family_id"))
        )

    if not event_service.event_belongs_to_current_user(retrieved_event, current_user):
        flash("You are not authorized to edit this event", "danger")
        return redirect(
            url_for("event.get_events", family_id=session.get("current_family_id"))
        )

    form = AddEventForm()

    if form.validate_on_submit():
        data, status = event_service.update_event(
            event=retrieved_event,
            event_date=form.date.data,
            event_name=form.name.data,
            location=form.location.data,
            description=form.description.data,
        )
        updated_event, message, category = (
            data.get("data"),
            data.get("message"),
            data.get("category"),
        )
        if status != 200:
            updated_event = retrieved_event
        flash(message, category)
        return redirect(url_for("event.get_events", family_id=updated_event.family_id))

    form.description.data = retrieved_event.description
    return render_template(
        "edit_event.html",
        title="Update Event details",
        event=retrieved_event,
        form=form,
    )
