from app.user.services import UserService
from http import HTTPStatus


def test_check_user_exists_false(app):
    """
    This function is a test case to verify the behavior of the `check_user_exists`
    method in the `UserService` class when a user does not exist in the system.

    Parameters:
    app : Any
        The test application instance, if required for the test context.

    Returns:
    bool
        True if the test passes, otherwise False.

    Raises:
    AssertionError
        If the assertion about the user's non-existence fails.
    """
    user_service = UserService()

    assert not user_service.check_user_exists(email="newuser@mail.com")


def test_check_user_exists_true(test_user_1):
    """
    Tests the functionality of verifying if a user exists by email.

    This function interacts with the UserService component to confirm
    whether a user with a specific email exists. It is designed specifically
    for testing purposes, relying on a predefined test user instance.

    Parameters:
    test_user_1: A preloaded test user object containing user details
                 such as email.

    Raises:
    AssertionError: If the service fails to correctly identify the existence
                    of the given user by their email.
    """
    service = UserService()

    assert service.check_user_exists(email=test_user_1.email)


def test_create_user(session):
    """
    Performs a test for user creation using the UserService.

    This function tests the creation of a new user through the UserService
    and verifies that the correct status and response message is returned.
    It ensures the user data is not null after creation.

    Parameters:
        session (Session): The database session used for the test.

    Raises:
        AssertionError: If the status, message, or data in the response
        do not meet the expected values.
    """
    service = UserService()

    response, status = service.create_user(
        name="new_user", email="ner_user@mail.com", password="newUserPass"
    )

    assert status == HTTPStatus.CREATED
    assert response["message"] == "User created successfully"
    assert response["data"] is not None


def test_create_user_conflicting_email(test_user_1):
    """
    Tests the behavior of the UserService when attempting to create a user
    with an email that already exists in the system. Ensures that the service
    returns the correct response and status code in the conflict case.

    Parameters
    ----------
    test_user_1 : User
        A pre-existing user object with an email that will be used to test
        the conflict scenario.

    Raises
    ------
    AssertionError
        If the behavior of the UserService does not match the expected
        response or status for a conflicting email case.
    """
    service = UserService()

    response, status = service.create_user(
        name="new_user", email=test_user_1.email, password="newUserPass"
    )

    assert status == HTTPStatus.CONFLICT
    assert response["message"] == "User already exists, try logging in"
    assert response["data"] is None


def test_create_user_error(session, monkeypatch):
    """
    Tests the behavior of the UserService.create_user method when an error occurs
    during database insertion. Mocks the database add method to simulate an exception
    and verifies that the correct error response and status code are returned.

    Args:
        session: Test session or fixture required for the test environment.
        monkeypatch: pytest's monkeypatch fixture used to modify or replace attributes.

    Raises:
        None
    """
    service = UserService()

    def mock_add(*args):
        raise Exception("Database error")

    # mock the database add method to raise an exception during the user creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_user(
        name="new_user_2", email="ner_user_2@mail.com", password="new2UserPass"
    )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Something went wrong creating user"
    assert response["data"] is None


def test_get_user_no_inputs(session):
    """
    Test the get_user() method for missing input parameters.

    This test case verifies the behavior of the get_user() method in the
    UserService class when neither an email nor a user_id is provided
    as inputs. It ensures the method returns the expected error message
    and status code, along with a null data value.

    Args:
        session: The database session or test session fixture used
            for testing.

    Raises:
        AssertionError: If the actual output of the tested function
            does not match the expected results.
    """
    service = UserService()
    response, status = service.get_user()
    assert status == HTTPStatus.BAD_REQUEST
    assert response["message"] == "Email or user_id is required"
    assert response["data"] is None


def test_get_user_by_email(test_user_1):
    """
    Tests the functionality of retrieving a user by email using the get_user method.
    The method should return the correct user data and a successful HTTP status if the
    provided email matches an existing user.

    Args:
        test_user_1: A mock user object with test data. The `email` attribute
            represented by this object is used to simulate a user lookup.

    Raises:
        AssertionError: If the returned status code does not match the expected
            success status, or the returned message and data are incorrect.
    """
    service = UserService()

    response, status = service.get_user(email=test_user_1.email)

    assert status == HTTPStatus.OK
    assert response["message"] == "User found"
    assert response["data"] == test_user_1


def test_get_user_by_id(test_user_1):
    """
    Test the functionality of retrieving a user by their ID.

    This test ensures that the `get_user` method in the `UserService`
    class correctly retrieves a user based on the provided user ID,
    and that the response includes the appropriate data and status.

    Parameters
    ----------
    test_user_1 : User
        A test user object with a valid user ID to simulate a user
        retrieval scenario.
    """
    service = UserService()

    response, status = service.get_user(user_id=test_user_1.user_id)

    assert status == HTTPStatus.OK
    assert response["message"] == "User found"
    assert response["data"] == test_user_1


def test_get_user_not_found(session):
    """
    Tests the behavior of the `get_user` method in the `UserService` when the requested user
    is not found.

    This function verifies that the method correctly responds with an appropriate HTTP status
    and error message when the specified user email does not exist in the system.

    Parameters
    ----------
    session : Any
        The database session or context within which the service operates.

    Raises
    ------
    AssertionError
        If the response or status returned by the `get_user` method are not as expected.
    """
    service = UserService()

    response, status = service.get_user(email="hello@mail.com")

    assert status == HTTPStatus.NOT_FOUND
    assert response["message"] == "User not found"
    assert response["data"] is None


def test_get_user_error(test_user_1, monkeypatch):
    """
    Unit test function to verify the behavior of the `get_user` method when a database-related
    error occurs. This test ensures that the method properly handles exceptions during user
    retrieval and returns an appropriate error response with a corresponding status.

    Parameters:
        test_user_1 (User): A test user object with attributes used for invoking the method.
        monkeypatch (MonkeyPatch): A utility to dynamically replace or mock objects for testing.
    """
    service = UserService()

    def mock_query(*args):
        raise Exception("Database error")

    # mock the database query method to raise an exception during the user retrieval
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_user(email=test_user_1.email)

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Something went wrong retrieving user"


def test_update_user(test_user_1):
    """
    Tests the functionality of updating a user's details using the UserService class.

    This test case ensures that the update_user method correctly modifies
    the provided user's properties such as name, password, and emailVerify
    status. It also verifies the expected output response and HTTP status
    from the update_user method.

    Args:
        test_user_1 (User): The user instance to be updated.

    Raises:
        AssertionError: If any of the assertions in the test case fail.

    Returns:
        None
    """
    service = UserService()

    response, status = service.update_user(
        user=test_user_1,
        first_name="new_name",
        password="new_password",
        emailVerify=True,
    )

    user = response["data"]
    assert status == HTTPStatus.OK
    assert user.first_name == "new_name"
    assert user.emailVerify
    assert user.check_password("new_password")
    assert response["message"] == "User updated successfully"


def test_update_user_error(test_user_1, monkeypatch):
    """
    Tests the behavior of the `update_user` method under error conditions when the database commit fails.
    This test ensures that the method handles exceptions appropriately and returns the expected error
    response and status code.

    Args:
        test_user_1: The mock user object to be updated.
        monkeypatch: A Pytest fixture that allows for dynamic replacement of attributes or methods.

    Raises:
        Exception: Simulates a database error when committing user updates.
    """
    service = UserService()

    def mock_commit(*args):
        raise Exception("Database error")

    # mock the database commit method to raise an exception during the user update
    monkeypatch.setattr(service.db, "commit", mock_commit)

    response, status = service.update_user(
        user=test_user_1,
        first_name="new_name",
        password="new_password",
        emailVerify=True,
    )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Something went wrong updating user information"
    assert response["data"] is None

    # undo the monkeypatch to avoid affecting other tests
    monkeypatch.undo()
