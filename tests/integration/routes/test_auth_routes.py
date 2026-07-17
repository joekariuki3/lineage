from http import HTTPStatus
from app.models import User
from flask import url_for
from flask_login import login_user, current_user
from app.auth.services import AuthService
from app.user.services import UserService
from app.services.service_base import service_response


def test_register_get(client, test_user_1):
    """
    Tests the behavior of the registration page in two scenarios:
    - When accessed by an unauthenticated user.
    - When accessed by an authenticated user, ensuring they are redirected to the main
    page.

    Attributes:
        client: A fixture that simulates a test client for making HTTP requests.
        test_user_1: A fixture representing a pre-existing test user.

    Args:
        client: Test client used to perform HTTP requests in the tests.
        test_user_1: Test user used to simulate authentication in the test.
    """
    response = client.get(url_for("auth.register"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Register" in response.data

    # if the user is authenticated, redirect to the main page
    login_user(test_user_1)
    response = client.get(url_for("auth.register"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Family Tree App" in response.data


def test_register_post(app, client, session):
    """
    Test the registration process functionality for new users by simulating a POST request
    to the registration endpoint and validating the database state and response content.

    Args:
        app: Flask application instance used to run the test context.
        client: Flask test client used to simulate HTTP requests to the application.
        session: Database session used to query and verify the application state.

    Raises:
        AssertionError: If any assertion regarding user registration, response content, or database
                        state fails.

    """
    # given
    user_data = {
        "name": "New_user",
        "email": "newuser@mail.com",
        "password": "newPassword",
        "confirm_password": "newPassword",
    }
    # when
    response = client.post(
        url_for("auth.register"), data=user_data, follow_redirects=True
    )

    # then
    assert response.status_code == HTTPStatus.OK
    assert b"Login" in response.data

    with app.app_context():
        user = session.query(User).filter_by(email=user_data["email"]).first()
        assert session.query(User).count() == 1
        assert user is not None
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
        assert user.check_password(user_data["password"])


def test_login_get(client, test_user_1):
    """
    Tests the "GET" behavior of the login route to ensure proper functionality
    and appropriate response status codes. It checks the page loading for
    unauthenticated users and the redirection to the family page for authenticated
    users.

    Args:
        client: Flask test client used for simulating requests.
        test_user_1: Instance of a test user data object pre-populated
            for login simulation.
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == HTTPStatus.OK
    assert b"Login" in response.data

    # if the user is authenticated, redirect to the family page
    login_user(test_user_1)
    response = client.get(url_for("auth.login"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data


def test_login_post(client, test_user_1):
    """
    This function tests the login functionality of an application using a test client.
    It checks whether the login endpoint behaves correctly when provided with invalid
    credentials and when provided with valid credentials.

    Parameters:
    client: The test client is used to simulate requests to the application.
    test_user_1: A test user object containing valid credentials for testing.

    Raises:
    AssertionError: If the expected response code or data for the login process does
    not match the actual responses.
    """
    # test login with incorrect credentials.
    invalid_user_data = {
        "email": "invalid_user@mail.com",
        "password": "invalidPassword",
    }
    response = client.post(
        url_for("auth.login"), data=invalid_user_data, follow_redirects=True
    )
    assert response.status_code == HTTPStatus.OK
    assert b"Invalid username or password" in response.data

    # test login with correct credentials.
    user_data = {"email": test_user_1.email, "password": "user1password"}
    response = client.post(url_for("auth.login"), data=user_data, follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data


def test_guest_no_guest_info(client, monkeypatch):
    """
    Tests the behavior of the guest endpoint when no guest information is
    available. This ensures that appropriate messages are displayed to
    the user in the absence of guest details and that the response status
    is correct.

    Args:
        client (FlaskClient): Test client used to simulate application
            requests.
        monkeypatch (pytest.MonkeyPatch): Utility used to mock or replace
            objects for testing purposes.
    """

    def mock_get_guest_info(*args):
        return None, None, None

    monkeypatch.setattr(AuthService, "get_guest_info", mock_get_guest_info)

    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert (
        b"Guest name, email and password are required. Contact admin" in response.data
    )
    assert b"Login" in response.data

    monkeypatch.undo()


def test_guest(client, test_guest_user_1):
    """
    Tests the guest user functionality of the application.

    This function is designed to validate the behavior of the system when a
    guest user attempts to access the guest-related endpoints. It ensures
    that the appropriate response is received, including verifying the
    presence of specific elements in the response data.

    Parameters:
    client
        The test client used to simulate requests to the application.
    test_guest_user_1
        A fixture or mock object representing a guest user instance for
        testing.

    Raises:
    AssertionError
        If any of the assertions fail, indicating that the application’s
        behavior does not match the expected results.
    """
    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data

    # if the guest user is authenticated, redirect to the family page
    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data


def test_guest_incorrect_credentials(client, test_guest_user_1, monkeypatch):
    """
    Tests the behavior of the guest login functionality when incorrect credentials
    are provided. A mocked version of the `get_guest_info` method is used to simulate
    the retrieval of guest information with an invalid password. Ensures the response
    is appropriate and provides the expected error message.

    Args:
        client (FlaskClient): The test client is used to simulate application requests.
        test_guest_user_1 (GuestUser): A test guest user object with predefined
            credentials.
        monkeypatch (MonkeyPatch): The test utility for dynamically modifying the
            behavior of objects or functions.

    Raises:
        AssertionError: If the expected response status or content does not match
            the actual results.
    """

    def mock_get_guest_info(*args):
        return test_guest_user_1.name, test_guest_user_1.email, "InvalidPassword"

    monkeypatch.setattr(AuthService, "get_guest_info", mock_get_guest_info)

    response = client.get(url_for("auth.guest"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Invalid username or password" in response.data
    assert b"Login" in response.data

    monkeypatch.undo()


def test_logout(client, test_user_1):
    """
    This function tests the logout functionality by logging in a user,
    triggering the logout route, and verifying the user has been logged out
    successfully.

    Args:
        client: A Flask test client instance used to send HTTP requests to the
            application.
        test_user_1: A mock user object representing a test user.

    Raises:
        AssertionError: If any of the assertions fail during the logout
            testing process.
    """
    login_user(test_user_1)

    assert current_user == test_user_1
    assert test_user_1.is_authenticated

    response = client.get(url_for("auth.logout"), follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert b"Login" in response.data
    assert b"Log out" not in response.data


def test_reset_password_request_get(client):
    """
    Tests the GET request to the reset password page.

    This function verifies that the reset password page is
    accessible via a GET request and checks for the expected
    content on the page to ensure the correct rendering.

    Args:
        client: A test client instance for simulating requests
            to the application.

    Raises:
        AssertionError: If the response status code is not HTTP OK,
            or if the expected content is not found in the response.

    Returns:
        None
    """
    response = client.get(url_for("auth.reset_password_request"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Reset Password" in response.data


def test_reset_password_request_get_authenticated(client, test_user_1):
    """
    Tests the reset password request page for an authenticated user.

    This function tests the scenario where an authenticated user tries
    to access the reset password request page.

    Arguments:
        client: The test client used to send requests to the application.
        test_user_1: The test user object used for authenticating the user.

    Returns:
        None
    """
    # log in the user
    client.post(
        url_for("auth.login"),
        data={"email": test_user_1.email, "password": "user1password"},
        follow_redirects=True,
    )

    response = client.get(url_for("auth.reset_password_request"), follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data


def test_reset_password_request_post(client, test_user_1):
    """
    Tests the POST request functionality for the password reset request endpoint to ensure
    that an email with instructions is sent when a valid email is provided.

    Parameters:
    client : FlaskClient
        A test client instance used to send mock requests to the application.
    test_user_1 : User
        A test user object with a valid email for testing the password reset request.

    Raises:
    AssertionError
        If the response status code is not 200 OK.
        If the success message is not found in the response data.
    """
    response = client.post(
        url_for("auth.reset_password_request"),
        data={"email": test_user_1.email},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        b"Check your email for the instructions to reset your password" in response.data
    )


def test_reset_password_request_post_invalid_email(client):
    """
    Tests the password reset request functionality with an invalid email input.

    This function validates that the application behaves as expected when
    a password reset request is made with an email address not linked to
    any account in the system. It verifies that the correct status code is
    returned and that the appropriate message is displayed to the user.

    Args:
        client: Flask test client used for making requests to the application.

    Raises:
        AssertionError: If the response does not fulfill the expected test
        conditions.
    """
    response = client.post(
        url_for("auth.reset_password_request"),
        data={"email": "invalid@mail.com"},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        b"Check your email for the instructions to reset your password" in response.data
    )


def test_reset_password_token_get_authenticated_user(client, test_user_1):
    """
    Performs a test to verify the reset password token functionality and the behavior of the
    authenticated user when accessing the reset password route.

    Parameters:
    client : FlaskClient
        Flask test client used to simulate requests to the application.

    test_user_1 : User
        A test user instance with associated credentials for the authentication
        process.

    Raises:
    AssertionError
        If the response status code does not match HTTPStatus.OK or if the expected
        response content is not found in the returned data.
    """
    client.post(
        url_for("auth.login"),
        data={"email": test_user_1.email, "password": "user1password"},
        follow_redirects=True,
    )
    response = client.get(
        url_for("auth.reset_password", token="test_token"), follow_redirects=True
    )
    assert response.status_code == HTTPStatus.OK
    assert b"Create Family" in response.data


def test_reset_password_token_get_invalid_token(client, test_user_1):
    """
    Tests the behavior of the reset_password endpoint when provided with an invalid token.

    This function verifies that the response status code is correct and that the
    appropriate error message is displayed when the token provided in the request
    is invalid or expired.

    Args:
        client: A fixture providing a test client for making requests to the
            application.
        test_user_1: A fixture representing a sample user used for testing.

    Raises:
        AssertionError: If the response status code or the response data does not
            meet the expected values.
    """
    response = client.get(
        url_for("auth.reset_password", token="invalid_token"), follow_redirects=True
    )
    assert response.status_code == HTTPStatus.OK
    assert b"Link expired. Request for a new link" in response.data
    assert b"Reset Password" in response.data


def test_reset_password_token_get_valid_token(client, app, test_user_1):
    """
    Tests the retrieval of a reset password page using a valid token.

    This function validates the functionality of accessing the reset password
    page when a valid reset password token is provided. It ensures that the
    response has an HTTP status code indicating success and verifies that the
    correct content is displayed on the password reset page.

    Args:
        client: A Flask test client to simulate an HTTP request.
        app: The Flask application instance providing the application context
            and configuration.
        test_user_1: A test user object used to generate a valid reset password
            token.

    Raises:
        AssertionError: If the response code is not HTTPStatus.OK or the page
            content does not include the keyword indicating the presence of
            the new password field.
    """
    token = test_user_1.get_reset_password_token(app.config["SECRET_KEY"])
    response = client.get(
        url_for("auth.reset_password", token=token), follow_redirects=True
    )
    assert response.status_code == HTTPStatus.OK
    assert b"New password" in response.data


def test_reset_password_token_post(client, app, test_user_1):
    """
    This function tests the reset password endpoint by making a POST request
    with a valid reset token and new password data. It validates the response
    status, checks that the success message appears, and verifies that the
    user's password has been updated correctly.

    Args:
        client (FlaskClient): The test client used to make HTTP requests to the app.
        app (Flask): The Flask application instance configured for testing.
        test_user_1 (User): A test user instance for which the password reset functionality
            is to be tested.

    Raises:
        AssertionError: If the response status is incorrect, if the success message is
            not present in the response, or if the password for the test user does not
            update to the new provided password.
    """
    token = test_user_1.get_reset_password_token(app.config["SECRET_KEY"])
    user_data_to_update = {
        "password": "newPassword123",
        "confirm_password": "newPassword123",
    }
    response = client.post(
        url_for("auth.reset_password", token=token),
        data=user_data_to_update,
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert b"User updated successfully" in response.data
    assert test_user_1.check_password("newPassword123")


def test_reset_password_token_post_error(client, app, test_user_1, monkeypatch):
    """
    Tests the behavior of the endpoint for resetting a user's password when there is an
    error updating the user's information. Simulates a server-side failure during the
    update process and verifies the response to ensure proper error handling and message
    display.

    Args:
        client: Flask test client used to simulate HTTP requests.
        app: Flask application instance providing configuration and context for the request.
        test_user_1: Test user object on which actions will be simulated during the test.
        monkeypatch: pytest fixture used to replace or modify the behavior of external
            dependencies or objects during the test.
    """

    def mock_update_user(*args, **kwargs):
        return service_response(
            500, "Something went wrong updating user information", "error", None
        )

    monkeypatch.setattr(UserService, "update_user", mock_update_user)

    token = test_user_1.get_reset_password_token(app.config["SECRET_KEY"])
    user_data_to_update = {
        "password": "newPassword123",
        "confirm_password": "newPassword123",
    }
    response = client.post(
        url_for("auth.reset_password", token=token),
        data=user_data_to_update,
        follow_redirects=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert not test_user_1.check_password("newPassword123")
    assert b"New password" in response.data
    assert b"Something went wrong updating user information" in response.data

    monkeypatch.undo()
