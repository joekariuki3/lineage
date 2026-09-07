import pytest
from flask import session as flask_session
from flask_login import logout_user

from app.auth.services import AuthService


@pytest.fixture
def user_with_one_family(session, test_user_1, test_family_1):
    """
    Creates a test user linked to a single test family and commits changes to the session.

    This pytest fixture updates the provided test family object to associate it
    with the given test user object. After modifying the family object, it commits
    the changes to the database session. It then yields the test user object for
    use in test functions. The fixture ensures that the test user is linked to a
    family within the database session during testing.

    Args:
        session: Database session instance to manage the lifecycle and commit
            changes to the database during the test.
        test_user_1: A test user object that represents the user to be linked to
            the family for testing purposes.
        test_family_1: A test family object that will be updated to associate
            itself with the provided test user.

    Yields:
        The test user object after the family has been associated and changes
        committed.
    """
    test_family_1.user_id = test_user_1.user_id
    session.commit()
    yield test_user_1

@pytest.fixture
def user_with_two_families(session, test_user_1, test_family_1, test_family_2):
    """
    Fixture to provide a user associated with two families in the database session.

    this fixture takes a predefined user and two family instances, associates
    these families with the user by assigning the user ID to the family records,
    commits the changes to the session, and yields the user along with the associated
    family instances for use in tests. This allows testing behaviors or features
    involving a user with multiple associated family records.

    Parameters:
        session: The database session for committing changes.
        test_user_1: A user instance to associate with the family records.
        test_family_1: The first family instance to associate with the user.
        test_family_2: The second family instance to associate with the user.

    Yields:
        Tuple containing the user instance and a list of family instances
        associated with the user ([test_family_1, test_family_2]).
    """
    test_family_1.user_id = test_user_1.user_id
    test_family_2.user_id = test_user_1.user_id
    session.commit()

    yield test_user_1, [test_family_1, test_family_2]

def test_authenticate_valid_user(app, test_user_1):
    """
    Authenticate and validate a user within a test request context by simulating a
    login process. The function asserts the response received from the authentication
    service and ensures the returned data aligns with expected results.

    Parameters:
    app : Flask
        The Flask application instance used for testing purposes.
    test_user_1 : User
        A mock or predefined user object that represents a valid test user.

    Raises:
    AssertionError
        If the status, message, category, or data in the response do not match
        the expected values.
    """
    with app.test_request_context():
        response = AuthService.authenticate("user1@mail.com", "user1password")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 200
        assert data['message'] == "Login successful"
        assert data['category'] == "success"
        assert data['data'].email == test_user_1.email

def test_authenticate_invalid_password(app, test_user_1):
    """
    Test the behavior of the authentication service when provided with an invalid password for a valid user.

    This function checks if the authentication service correctly identifies and rejects an invalid
    password, returning the appropriate error message and HTTP status code.

    Args:
        app: The application object providing the test request context.
        test_user_1: A valid user object pre-registered in the test database.

    Raises:
        AssertionError: If the authentication service does not return the expected results.

    """
    with app.test_request_context():
        response = AuthService.authenticate(test_user_1.email, "wrongpassword")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 403
        assert data['message'] == "Invalid username or password"
        assert data['data'] is None

def test_authenticate_nonexistent_user(app):
    """
    Test the authentication process for a nonexistent user. This function verifies
    that the AuthService correctly handles a request to authenticate a user who
    does not exist in the system.

    Args:
        app: The Flask application instance used to create a test request context.

    Raises:
        AssertionError: If the AuthService does not return the expected response
        values, including the proper status code and error message format.
    """
    with app.test_request_context():
        response = AuthService.authenticate("nouser@example.com", "any")

        assert isinstance(response, tuple)
        data, status = response[0], response[1]
        assert status == 403
        assert data['message'] == "Invalid username or password"
        assert data['data'] is None

def test_get_guest_info(app):
    """
    Tests the functionality of retrieving guest information from the AuthService class.

    This function validates that the AuthService's `get_guest_info` method correctly returns
    guest-related information. It compares the returned guest attributes with the application's
    configured values for a guest (name, email, and password).

    Parameters:
    app : Flask
        The Flask application instance with configuration containing guest credentials.

    Raises:
    AssertionError
        If the returned guest information is None or does not match the expected configuration values.
    """
    service = AuthService()
    guest_info = service.get_guest_info()
    assert guest_info is not None
    assert guest_info == (app.config['GUEST_NAME'], app.config['GUEST_EMAIL'], app.config['GUEST_PASSWORD'] )

def test_set_current_family_id_one_family(app, user_with_one_family):
    """
    Tests the `set_current_family_id` functionality for a user with one associated
    family. This ensures that the `current_family_id` is correctly set in the user's
    session and matches the single family's ID.

    Args:
        app: A Flask application configured for testing.
        user_with_one_family: A user fixture representing a user with exactly one
            associated family.

    Raises:
        AssertionError: If `current_family_id` is not set in the session or does not
        match the expected family ID.
    """
    with app.test_request_context():
        AuthService.authenticate(email=user_with_one_family.email, password="user1password")
        AuthService.set_current_family_id()

        assert 'current_family_id' in flask_session
        assert flask_session['current_family_id'] == user_with_one_family.families[0].family_id
        logout_user()

def test_set_current_family_id_unauthenticated_user():
    """
    Represents a test function that ensures the behavior of the `set_current_family_id` method
    from the `AuthService` when an unauthenticated user attempts to invoke it. This function
    evaluates that the method correctly returns `None` for an unauthenticated user.

    Raises:
        AssertionError: If the `set_current_family_id` method does not return `None`.
    """
    service = AuthService()
    assert service.set_current_family_id() is None

def test_set_current_family_id_multiple_with_param(app, user_with_two_families):
    """
    Tests the ability to switch the current family context for a user with multiple families.

    This function verifies that the `set_current_family_id` method correctly updates the
    current family ID in the session for an authenticated user with two families. It ensures
    that the session reflects the updated family ID and validates the status after logout.

    Parameters:
        app (Flask): The Flask application context used for testing.
        user_with_two_families (Tuple[User, List[Family]]): A tuple containing a user object and
            a list of two family objects associated with the user.

    Raises:
        AssertionError: If the current family ID is not correctly set in the session or
            if session verification fails after the method call.
    """
    user, families = user_with_two_families
    with app.test_request_context():
        AuthService.authenticate(email=user.email, password="user1password")
        AuthService.set_current_family_id(current_family_id=families[1].family_id)

        assert 'current_family_id' in flask_session
        assert flask_session['current_family_id'] == families[1].family_id
        logout_user()

def test_set_current_family_id_multiple_without_param(app, user_with_two_families):
    """
    Tests the behavior of the set_current_family_id method when called without any
    parameters, verifying that it does not set a current_family_id in the session
    and returns the flask_session unchanged. Additionally, validates the correct
    operation of user authentication and logout mechanisms.

    Args:
        app: Flask application instance used to create a test request context.
        user_with_two_families: A tuple containing a user instance with two
            associated families and additional related data, if any.

    Raises:
        AssertionError: If the current_family_id is present in flask_session or
            if the returned value of set_current_family_id does not match the
            actual flask_session.
    """
    user, _ = user_with_two_families
    with app.test_request_context():
        AuthService.authenticate(email=user.email, password="user1password")
        result = AuthService.set_current_family_id()  # no param

        assert 'current_family_id' not in flask_session
        assert result == flask_session
        logout_user()