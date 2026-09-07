from datetime import datetime
from http import HTTPStatus

from flask import url_for

from app.event.services import EventService
from app.models.event import Event
from app.services.service_base import service_response
from tests.utils import login_test_user_1


def test_add_event_get_user_no_family(client, test_user_1):
    """
    Tests adding an event when the user does not belong to any family.

    This test ensures that a user who attempts to access the event
    creation page without being part of a family is properly redirected
    and notified that at least one family is required to add an event.
    Additionally, it verifies that the response includes a prompt
    to create a family.

    Parameters:
    client :
        A test client instance for simulating HTTP requests to the
        application.
    test_user_1 :
        The test user for this scenario, which logs in before
        attempting to view the event page.
    """
    login_test_user_1(client, test_user_1)
    response = client.get(url_for("event.add_event"), follow_redirects=True)

    assert response.status_code == 200
    assert b"At least one family is required to add an event" in response.data
    assert b"Create Family" in response.data

def test_add_event_get(client, test_user_and_family):
    """
    Tests the 'add_event' functionality by verifying that the 'Add Event'
    page is accessible for a logged-in user and returns the expected
    response content.

    Arguments:
        client: A test client instance used for making requests in a controlled
        testing environment.
        test_user_and_family: A fixture that returns a tuple containing a test
        user and their associated family.

    Raises:
        AssertionError: If the status code of the response is not 200 or if the
        response data does not include the expected text "Add Event".
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    response = client.get(url_for("event.add_event"), follow_redirects=True)

    assert response.status_code == 200
    assert b"Add Event" in response.data

def test_add_event_post(client, app, session, test_user_and_family):
    """
    Tests the creation of an event through a POST request to the event endpoint.

    The function simulates the process of creating a new event in a web application,
    ensuring that the event creation functionality works as expected and that the
    database updates correctly with the new event data.

    Parameters:
    client : flask.testing.FlaskClient
        The Flask test client used to simulate HTTP requests to the application.
    app : flask.Flask
        The Flask application instance used for testing.
    session : sqlalchemy.orm.session.Session
        The SQLAlchemy session object used to interact with the database during tests.
    test_user_and_family : Tuple[User, Family]
        A tuple containing a test user instance and associated family instance for testing.

    Raises:
    AssertionError
        If the response status code does not match the expected value, or the required content
        is not present in the response data, or the event is not properly persisted in the database.
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    event_data = {
        "name": "Test Event",
        "date": datetime(2025, 12, 25),
        "family": family.family_id,
        "description": "Test Description",
        "location": "Test Location"
    }
    response = client.post(url_for("event.add_event"), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event created successfully" in response.data
    assert b"Test Event" in response.data

    with app.app_context():
        assert session.query(Event).count() == 1

def test_add_event_post_error(client, app, session, test_user_and_family, monkeypatch):
    """
    Tests the behavior of adding an event when an error occurs during the event
    creation service call.

    Parameters:
    client
        Flask test client used to simulate HTTP requests.
    app
        Flask application fixture to manage application context.
    session
        Database session fixture for querying and committing transactions.
    test_user_and_family
        Tuple containing a test user object and a corresponding test family
        object.
    monkeypatch
        pytest's monkeypatching utility for mocking functions or methods.

    Raises:
    AssertionError
        Raised if the test assertions fail.

    This test verifies the following:
    - When the `create_event` method in `EventService` returns an error response,
      the system displays an appropriate error message on the response page.
    - No new event record is created in the database when an error occurs during
      the event creation process.
    """
    user, family = test_user_and_family
    family.user_id = user.user_id
    login_test_user_1(client, user)

    def mock_create_event(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error creating event",
            "danger",
            None
        )
    monkeypatch.setattr(EventService, "create_event", mock_create_event)

    event_data = {
        "name": "Test Event",
        "date": datetime(2025, 12, 25),
        "family": family.family_id,
        "description": "Test Description",
        "location": "Test Location"
    }
    response = client.post(url_for("event.add_event"), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error creating event" in response.data
    assert b"Add Event" in response.data

    with app.app_context():
        assert session.query(Event).count() == 0

def test_get_events_no_events(client, test_user_and_family):
    """
    Tests the behavior of the 'get_events' endpoint when no events are present for
    a family. It checks that the correct message is displayed for both upcoming
    and past events when the events list is empty.

    Args:
        client: A Flask test client used to simulate HTTP requests in the test.
        test_user_and_family: A fixture providing a test user and their
            associated family for testing purposes.

    Raises:
        AssertionError: If the test conditions are not met.

    Test Conditions:
    - Verifies that the response status code is 200.
    - Checks if the message "No Upcoming Event at the moment" is present in the
      response when no upcoming events exist.
    - Checks if the message "No Past Event at the moment" is present in the
      response when no past events exist.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)

    response = client.get(url_for("event.get_events", family_id=family.family_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"No Upcoming Event at the moment" in response.data
    assert b"No Past Event at the moment" in response.data

def test_get_events(client, test_user_and_family, test_event_1):
    """
    This function tests the behavior of retrieving events associated with a family ID
    after authenticating a test user. It ensures the correct response status code is
    returned and verifies the presence of specific event data in the response.

    Args:
        client: A test client instance used to simulate HTTP requests within the
            test environment.
        test_user_and_family: A fixture providing a test user and their associated
            family setup for the test case.
        test_event_1: A fixture representing a test event to be linked to the
            family's ID during the test.

    Raises:
        AssertionError: If the expected status code or event data is not found
            in the response.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)

    response = client.get(url_for("event.get_events", family_id=family.family_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"event_1" in response.data

def test_delete_event(client, session, app, test_user_and_family, test_event_1):
    """
    Tests the deletion of an event associated with a family and verifies that the event
    is removed from the database and that the appropriate success message is displayed.

    Parameters:
        client: The test client used to simulate HTTP requests.
        session: The database session used for querying and managing data integrity.
        app: The Flask application instance providing the application context.
        test_user_and_family: A fixture returning a test user and their associated family.
        test_event_1: A fixture providing a test event object.

    Raises:
        AssertionError: If the event deletion operation or related conditions fail.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)

    # before deletion assert event exists
    with app.app_context():
        assert session.query(Event).count() == 1

    response = client.post(url_for("event.delete_event", event_id=test_event_1.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"Event deleted successfully" in response.data

    # assert event does not exist after deletion
    with app.app_context():
        assert session.query(Event).count() == 0

def test_delete_event_error(client, session, app, test_user_and_family, test_event_1, monkeypatch):
    """
    Test the behavior of event deletion when an error occurs in the service layer.

    This function simulates the scenario where a user tries to delete an event, but the
    deletion fails due to an internal server error. It verifies that the event remains
    intact in the database and proper error messages are displayed to the user.

    Parameters:
        client: FlaskClient
            The testing client is used to simulate HTTP requests during tests.
        session: Session
            The SQLAlchemy session to query and manipulate the database.
        app: Flask
            The Flask application instance used during test execution.
        test_user_and_family: Tuple[User, Family]
            A tuple containing the test user and their corresponding family.
        test_event_1: Event
            The event instance representing the test event to be deleted.
        monkeypatch: MonkeyPatch
            An object used to modify or replace attributes and functions during testing.

    Raises:
        AssertionError: If any assertion regarding HTTP response, error message, or
            event existence in the database fails.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)

    # before deletion assert event exists
    with app.app_context():
        assert session.query(Event).count() == 1

    def mock_delete_an_event(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error deleting event",
            "danger",
            None
        )
    monkeypatch.setattr(EventService, "delete_an_event", mock_delete_an_event)

    response = client.post(url_for("event.delete_event", event_id=test_event_1.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"Error deleting event" in response.data
    assert b"event_1" in response.data

    # assert event still exists after an error in deletion
    with app.app_context():
        assert session.query(Event).count() == 1

    monkeypatch.undo()

def test_edit_event_get_non_existing_event(client, test_user_and_family):
    """
    Tests the behavior of the `edit_event` route when attempting to retrieve a non-existing event.

    This test ensures that when a user tries to access the event editing page for an event that does not exist,
    the application handles the situation gracefully by returning a response with status code 200 and
    providing a message indicating that the event was not found.

    Parameters:
    client: The test client used to simulate HTTP requests.
    test_user_and_family: A fixture that provides a test user and their associated family structure.

    Raises:
    AssertionError: If the response status code is not 200 or the expected "Event not found" message
                    is not present in the response data.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)

    response = client.get(url_for("event.edit_event", event_id=999999), follow_redirects=True)

    assert response.status_code == 200
    assert b"Event not found" in response.data

def test_edit_event_get_event_not_owned_by_user(client, test_user_and_family, test_event_2):
    """
    Tests that a user cannot access the edit event page for an event not owned by them. It ensures that a proper
    unauthorized message is displayed when attempting to edit another user's event.

    Parameters:
    client: FlaskClient
        The test client used to make requests to the application.
    test_user_and_family: tuple
        A tuple containing the test user object and associated family information.
    test_event_2: Event
        An event instance that is not owned by the test user.

    Raises:
    AssertionError
        If the response status code is not 200, or the unauthorized message is not present in the response data.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)
    response = client.get(url_for("event.edit_event", event_id=test_event_2.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"You are not authorized to edit this event" in response.data

def test_edit_event_get(client, test_user_and_family, test_event_1):
    """
    Tests the GET method of the edit_event view.

    This function logs in a test user, sends a GET request to the edit_event
    endpoint with a specified event ID, and verifies the HTTP response status
    code and the presence of specific content in the response data.

    Args:
        client: Flask test client for sending requests to the application.
        test_user_and_family: Tuple containing a test user object and a test
            family object.
        test_event_1: Test event object whose details are to be fetched.

    Raises:
        AssertionError: If the response code or content does not match
            expected values.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)

    response = client.get(url_for("event.edit_event", event_id=test_event_1.event_id), follow_redirects=True)

    assert response.status_code == 200
    assert b"Update Event details" in response.data
    assert b"event_1" in response.data

def test_edit_event_post(client, test_user_and_family, test_event_1):
    """
    Tests the functionality of editing an event using a POST request. This test checks if an authenticated user can update an event's details successfully and if the expected
    changes are reflected in the response. It includes verifying success messages, updated event details, and the HTTP response status.

    Parameters:
        client: FlaskClient
            The test client used to simulate HTTP requests.
        test_user_and_family: Tuple[User, Family]
            A tuple containing a test user and their associated family.
        test_event_1: Event
            The test event that will be updated.

    Raises:
        AssertionError: If the response status code, success message, or updated event details
            do not match the expected results.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)
    event_data = {
        "name": "Updated Event",
        "date": datetime(2025, 12, 25),
        "family": test_event_1.family_id,
        "description": "Updated Description",
        "location": "Updated Location"
    }
    response = client.post(url_for("event.edit_event", event_id=test_event_1.event_id), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Event updated successfully" in response.data
    assert b"Updated Event" in response.data

def test_edit_event_post_error(client, test_user_and_family, test_event_1, monkeypatch):
    """
    Tests the behavior of the edit_event POST route when an error occurs during
    event update. This function simulates a failure in the event update service,
    intercepts the update method of EventService to return an error response,
    and verifies the client's response and behavior when attempting to update an
    event under these conditions.

    Args:
        client: Flask test client used to interact with the application during
            tests.
        test_user_and_family: Tuple consisting of test user information and family
            associated with the user.
        test_event_1: An event object representing a test event being edited.
        monkeypatch: Pytest-provided fixture for dynamically modifying objects or
            methods during tests.

    Raises:
        AssertionError: Raised if assertions within the test fail, indicating
            incorrect behavior or unexpected results.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)

    def mock_update_event(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error updating event",
            "danger",
            None
        )
    monkeypatch.setattr(EventService, "update_event", mock_update_event)

    event_data = {
        "name": "Updated Event",
        "date": datetime(2025, 12, 25),
        "family": test_event_1.family_id,
        "description": "Updated Description",
        "location": "Updated Location"
    }
    response = client.post(url_for("event.edit_event", event_id=test_event_1.event_id), data=event_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error updating event" in response.data
    assert b"event_1" in response.data # the event name should not change

    monkeypatch.undo()