from datetime import datetime

from flask_login import current_user

from app.extensions import db
from app.models import Event, User
from app.services.service_base import service_response


class EventService:

    def __init__(self, db_session=None):
        self.db = db_session or db.session

    def create_event(self, event_date: datetime, event_name: str, family_id: int, location: str | None, description: str | None) -> tuple[dict, int]:
        """
        creates a new event instance and saves it to the database.

        Args:
            event_date (str): The date of the event.
            event_name (str): The name of the event.
            family_id (int): The ID of the family that the event belongs to.
            location (Union[str, None]): The location of the event.
            description (Union[str, None]): A description of the event.

        Returns:
            Tuple[dict, int]: A service response containing the event instance and a status code.
        """
        try:
            event = Event(
            event_date=event_date,
            event_name=event_name,
            location=location,
            description=description,
            family_id=family_id)

            self.db.add(event)
            self.db.commit()

            return service_response(201, "Event created successfully", "success", event)
        except Exception as e:
            print(f"Error creating event: {e!s}")
            self.db.rollback()
            return service_response(500, "Error creating event", "danger", None)

    def get_upcoming_events(self, family_id: int) -> tuple[dict, int]:
        """
        Retrieves upcoming events for a specific family.

        Args:
            family_id (int): The ID of the family.

        Returns:
            Tuple[dict, int]: A service response containing the list of upcoming events and a status code.
        """
        try:
            current_time = datetime.now()
            events = self.db.query(Event).order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date>=current_time ).all()
            if not events:
                return service_response(404, "No upcoming events found", "warning", None)
            return service_response(200, "Upcoming events retrieved successfully", "success", events)
        except Exception:
            return service_response(500, "Error retrieving upcoming events", "danger", None)

    def get_past_events(self, family_id: int) -> tuple[dict, int]:
        """
        Retrieves past events for a specific family, ordered by the most recent events first.

        Args:
            family_id (int): The ID of the family.

        Returns:
            Tuple[dict, int]: A service response containing the list of past events and a status code.
        """
        try:
            current_time = datetime.now()
            events = self.db.query(Event).order_by(Event.event_date.desc()).filter_by(family_id=family_id).filter(Event.event_date<=current_time).all()
            if not events:
                return service_response(404, "No past events found", "warning", None)
            return service_response(200, "Past events retrieved successfully", "success", events)
        except Exception:
            return service_response(500, "Error retrieving past events", "danger", None)

    def get_event(self, event_id: int) -> tuple[dict, int]:
        """
        Retrieves an event by its ID.

        Args:
            event_id (int): The ID of the event.

        Returns:
            Tuple[dict, int]: A service response containing an object with a message, category, and data(event|None), and a status code.
        """
        try:
            event = self.db.get(Event, event_id)
            if not event:
                return service_response(404, "Event not found", "warning", None)
            return service_response(200, "Event retrieved successfully", "success", event)
        except Exception:
            return service_response(500, "Error retrieving event", "danger", None)

    @staticmethod
    def event_belongs_to_current_user(event: Event, user: User)-> bool:
        """
        checks if an event belongs to the current user by checking if the event's family id is in the user's family ids.

        Args:
            event (Event): The event to check.
            user (User): The current user.

        Returns:
            bool: True if the event belongs to the current user, False otherwise.
        """
        users_family_ids = [family.family_id for family in user.families]
        return event.family_id in users_family_ids

    def delete_an_event(self, event_id: int) -> tuple[dict, int]:
        """
        Deletes an event from the database.

        Args:
            event_id (int): The ID of the event to delete.

        Returns:
            Tuple[dict, int]: A service response containing an object with a message, category, data, and a status code.
        """
        try:
            data, code = self.get_event(event_id)
            if code != 200:
                return data, code

            event = data.get('data')

            if not self.event_belongs_to_current_user(event, current_user):
                return service_response(403, "You are not authorized to delete this event", "danger", None)

            self.db.delete(event)
            self.db.commit()
            return service_response(200, "Event deleted successfully", "success", None)
        except Exception:
            self.db.rollback()
            return service_response(500, "Error deleting event", "danger", None)

    def update_event(self, event: Event, event_date: datetime, event_name: str, location: str, description: str) -> tuple[dict, int]:
        """
        updates an event in the database.

        Args:
            event (Event): The event to update.
            event_date (str): The date of the event.
            event_name (str): The name of the event.
            location (str): The location of the event.
            description (str): A description of the event.

        Returns:
            Tuple[dict, int]: A service response containing the updated event instance and a status code.
        """
        try:
            event.event_date = event_date
            event.event_name = event_name
            event.location = location
            event.description = description

            self.db.commit()
            return service_response(200, "Event updated successfully", "success", event)
        except Exception:
            self.db.rollback()
            self.db.refresh(event)  # Refresh from DB to discard in-memory changes
            return service_response(500, "Error updating event", "danger", None)