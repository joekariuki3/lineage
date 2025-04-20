from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from . import bp
from datetime import datetime
from app.models.event import Event
from .forms import AddEventForm
from app.extensions import db

@bp.route('/event/', methods=['POST', 'GET'])
@login_required
def add_event():
    form = AddEventForm()
    if form.validate_on_submit():
        date = form.date.data
        name = form.name.data
        location = form.location.data
        description = form.description.data
        # get family id
        family_id = request.form.get('family')
        newEvent = Event(event_date=date,
                     event_name=name,
                     location=location,
                     description=description,
                     family_id=family_id)
        db.session.add(newEvent)
        db.session.commit()
        flash(f'{newEvent.event_name} added Successfully', 'success')
        return(redirect(url_for('event.get_events', family_id=newEvent.family_id)))
    return render_template('add_event.html', title='Add Event', form=form)

@bp.route('/event/<family_id>', methods=['POST', 'GET'])
@login_required
def get_events(family_id):
    currentTime = datetime.now()
    upcomingEvents = Event.query.order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date>=currentTime ).all()
    pastEvents = Event.query.order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date<=currentTime ).all()
    return render_template('events.html', upcomingEvents=upcomingEvents, pastEvents=pastEvents)

@bp.route('/delete/event/<event_id>')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    user_ids = [family.family_id for family in current_user.families]
    if event.family_id in user_ids:
        db.session.delete(event)
        db.session.commit()
        flash(f'{event.event_name} Deleted successfully', 'info')
        return redirect(url_for('event.get_events', family_id=event.family_id))
    flash('You dont have permission to delete this event', 'warning')
    return redirect(url_for('event.get_events', family_id=event.family_id))

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

