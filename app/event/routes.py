from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from . import bp
from datetime import datetime
from app.models.event import Event
from .forms import AddEventForm
from app.extensions import db
from .services import create_event, get_upcoming_events, get_past_events, delete_an_event

@bp.route('/event/', methods=['POST', 'GET'])
@login_required
def add_event():
    families = [family for family in current_user.families]
    if len(families) < 1:
        flash('At least one family is required to add an event', 'warning')
        return redirect(url_for('family.index'))

    form = AddEventForm()
    if form.validate_on_submit():
        data, status = create_event(
            event_date=form.date.data,
            event_name=form.name.data,
            family_id=request.form.get('family'),
            event_location=form.location.data,
            event_description=form.description.data
            )

        event, message, category = data.get('data'), data.get('message'), data.get('category')

        if status != 201:
            flash(message, category)
            return render_template('add_event.html', title='Add Event', form=form)

        flash(message, category)
        return(redirect(url_for('event.get_events', family_id=event.family_id)))
    return render_template('add_event.html', title='Add Event', form=form, families=families)

@bp.route('/event/<family_id>', methods=['POST', 'GET'])
@login_required
def get_events(family_id):
    data, status = get_upcoming_events(family_id)
    upcoming_events, message, category = data.get('data', []), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)
    elif not upcoming_events:
        flash(message, category)

    data, status = get_past_events(family_id)
    past_events, message, category = data.get('data', []), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)
    elif not past_events:
        flash(message, category)

    return render_template('events.html', upcomingEvents=upcoming_events, pastEvents=past_events)

@bp.route('/delete/event/<event_id>')
@login_required
def delete_event(event_id):
    data, status = delete_an_event(event_id)

    event, message, category = data.get('data'), data.get('message'), data.get('category')

    if status != 200:
        flash(message, category)
    elif not event:
        flash(message, category)
    else:
        flash(message, category)

    return redirect(url_for('event.get_events', family_id=current_user.current_family_id))

@bp.route('/edit/event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = AddEventForm()
    user_ids = [family.family_id for family in current_user.families]
    if form.validate_on_submit() and event.family_id in user_ids:
        event.event_date = form.date.data
        event.event_name = form.name.data
        event.location = form.location.data
        event.description = form.description.data
        db.session.commit()
        flash(f'{event.event_name} details Updated', 'success')
        return redirect(url_for('event.get_events', family_id=event.family_id))
    form.description.data = event.description
    return render_template('edit_event.html', title='Update Event details', event=event, form=form)

