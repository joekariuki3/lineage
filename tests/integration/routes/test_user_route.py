from http import HTTPStatus

from flask import url_for

from app.user.services import UserService
from tests.utils import login_test_user_1


def test_user_profile_unauthenticated_user(client):
    """
    Tests the behavior of the user profile route for an unauthenticated user.

    This function simulates an unauthenticated user attempting to access the user
    profile page. It ensures that the server responds with a redirect to the login
    page and provides a relevant informational message.

    Parameters:
    client
        The test client instance used to simulate requests to the application.

    Raises:
    AssertionError
        If the actual HTTP response status code does not match the expected value
        or if the informational message is not present in the response data.
    """
    response = client.get(url_for("user.user_profile"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Please log in to access this page." in response.data
    assert b"Login" in response.data

def test_user_profile(client, test_user_1):
    """
    Tests the user profile functionality for retrieving and displaying
    the profile data of a logged-in test user.

    Args:
        client: Flask test client used to make requests to the application.
        test_user_1: Test user object used for authentication and testing.

    Raises:
        AssertionError: If the status code of the response is not OK (200).
        AssertionError: If the expected test user's name is not found in the
        response data.
    """
    login_test_user_1(client, test_user_1)
    response = client.get(url_for("user.user_profile"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Test User 1" in response.data

def test_edit_profile_unauthenticated_user(client):
    """
    Tests the edit_profile view for unauthenticated users and verifies redirection to the login page
    with an appropriate message.

    Args:
        client: Flask test client used to simulate HTTP requests in the test.

    Raises:
        AssertionError: If the response does not meet any of the expected conditions.
    """
    response = client.get(url_for("user.edit_profile"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Please log in to access this page." in response.data
    assert b"Login" in response.data

def test_edit_profile_get(client, test_user_1):
    """
    Tests the GET request for the "edit_profile" route to ensure it correctly renders
    the "Edit Profile" page when accessed by an authenticated user.

    Parameters:
    client : FlaskClient
        A test client instance for making requests to the application.
    test_user_1 : User
        A mock user to simulate authenticated access.

    Raises:
    AssertionError
        If any of the assertions checking response status or content fail.
    """
    login_test_user_1(client, test_user_1)
    response = client.get(url_for("user.edit_profile"))
    assert response.status_code == HTTPStatus.OK
    assert b"Edit Profile" in response.data
    assert b"Test User 1" in response.data

def test_edit_profile_post(client, test_user_1):
    """
    Tests the functionality of updating a user profile through a POST request.
    This function verifies if the profile update performs correctly, including
    returning the proper HTTP status code and updating the user data in the
    response.

    Parameters:
    client : flask.testing.FlaskClient
        A test client instance for simulating requests to the application.
    test_user_1 : User
        A pre-defined test user object used for login and testing purposes.
    """
    login_test_user_1(client, test_user_1)
    data = {"name": "updated new name", "email": "new@mail.com"}
    response = client.post(url_for("user.edit_profile"), data=data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"User updated successfully" in response.data
    assert b"updated new name" in response.data
    assert b"new@mail.com" in response.data

def test_edit_profile_post_error(client, test_user_1, monkeypatch):
    """
    Tests the behavior of the "edit profile" functionality when a database commit error is simulated, ensuring that
    the appropriate failure messages are displayed and the user's profile remains unchanged.

    Arguments:
        client: Flask test client used to simulate HTTP requests.
        test_user_1: Mock user object used for testing.
        monkeypatch: Utility used to modify or replace code during testing.

    Raises:
        Exception: Mocked commit error triggered intentionally to test error handling.

    """
    login_test_user_1(client, test_user_1)

    service = UserService()

    def mock_commit(*args):
        raise Exception("Mocked commit error")
    monkeypatch.setattr(service.db, "commit", mock_commit)

    data = {"name": "new_name", "email":"new@mail.com"}
    response = client.post(url_for("user.edit_profile"), data=data, follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert b"Something went wrong updating user information" in response.data
    assert b"Test User 1" in response.data # the user's name has not changed

    monkeypatch.undo()