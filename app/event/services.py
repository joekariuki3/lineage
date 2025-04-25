from app.extensions import db
from app.models.event import Event
from app.services.service_base import service_response
from typing import Tuple, Union

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
        location=event_location,
        description=event_description,
        family_id=family_id)

        db.session.add(event)
        db.session.commit()

        return service_response(201, "Event created successfully", "success", event)
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        db.session.rollback()
        return service_response(500, "Error creating event", "danger", None)