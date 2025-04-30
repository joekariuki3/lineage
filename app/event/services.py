from app.extensions import db
from app.models import Event, User
from app.services.service_base import service_response
from datetime import datetime
from typing import Tuple, Union
from flask_login import current_user

def create_event(event_date: str, event_name: str, family_id: int, event_location: Union[str, None], event_description: Union[str, None]) -> Tuple[dict, int]:
    """
    Creates a new event instance and saves it to the database.

    Args:
        event_date (str): The date of the event.
        event_name (str): The name of the event.
        family_id (int): The ID of the family that the event belongs to.
        event_location (Union[str, None]): The location of the event.
        event_description (Union[str, None]): A description of the event.

    Returns:
        Tuple[dict, int]: A service response containing the event instance and a status code.
    """
    try:
        event = Event(
        event_date=event_date,
        event_name=event_name,
        event_location=event_location,
        event_description=event_description,
        family_id=family_id)

        db.session.add(event)
        db.session.commit()

        return service_response(201, "Event created successfully", "success", event)
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        db.session.rollback()
        return service_response(500, "Error creating event", "danger", None)

def get_upcoming_events(family_id: int):
    """
    Retrieves upcoming events for a specific family.

    Args:
        family_id (int): The ID of the family.

    Returns:
        Tuple[dict, int]: A service response containing the list of upcoming events and a status code.
    """
    try:
        current_time = datetime.now()
        events = db.session.query(Event).order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date>=current_time ).all()
        if not events:
            return service_response(200, "No upcoming events found", "warning", [])
        return service_response(200, "Upcoming events retrieved successfully", "success", events)
    except Exception as e:
        return service_response(500, "Error retrieving upcoming events", "danger", None)

def get_past_events(family_id: int):
    """
    Retrieves past events for a specific family, ordered by the most recent events first.

    Args:
        family_id (int): The ID of the family.

    Returns:
        Tuple[dict, int]: A service response containing the list of past events and a status code.
    """
    try:
        current_time = datetime.now()
        events = db.session.query(Event).order_by(Event.event_date.desc()).filter_by(family_id=family_id).filter(Event.event_date<=current_time).all()
        if not events:
            return service_response(200, "No past events found", "warning", [])
        return service_response(200, "Past events retrieved successfully", "success", events)
    except Exception as e:
        return service_response(500, "Error retrieving past events", "danger", None)

def get_event(event_id: int) -> Tuple[dict, int]:
    """
    Retrieves an event by its ID.

    Args:
        event_id (int): The ID of the event.

    Returns:
        Tuple[dict, int]: A service response containing object with a message, category, and data(event|None), and a status code.
    """
    try:
        event = db.session.query(Event).get(event_id)
        if not event:
            return service_response(200, "Event not found", "warning", None)
        return service_response(200, "Event retrieved successfully", "success", event)
    except Exception as e:
        return service_response(500, "Error retrieving event", "danger", None)

def event_belongs_to_current_user(event: Event, user: User)-> bool:
    """
    Checks if an event belongs to the current user by checking if the event's family id is in the user's family ids.

    Args:
        event (Event): The event to check.
        user (User): The current user.

    Returns:
        bool: True if the event belongs to the current user, False otherwise.
    """
    users_family_ids = [family.family_id for family in user.families]
    return event.family_id in users_family_ids

def delete_an_event(event_id: int) -> Tuple[dict, int]:
    """
    Deletes an event from the database.

    Args:
        event_id (int): The ID of the event to delete.

    Returns:
        Tuple[dict, int]: A service response containing a object with a message, category, data, and a status code.
    """
    try:
        data, code = get_event(event_id)
        if code != 200:
            return data, code

        event = data.get('data')
        if not event:
            return data, code

        if not event_belongs_to_current_user(event, current_user):
            return service_response(403, "You are not authorized to delete this event", "danger", None)

        db.session.delete(event)
        db.session.commit()
        return service_response(200, "Event deleted successfully", "success", None)
    except Exception as e:
        db.session.rollback()
        return service_response(500, f"Error deleting event {str(e)}", "danger", None)