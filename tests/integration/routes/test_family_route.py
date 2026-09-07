from datetime import datetime
from http import HTTPStatus

from flask import url_for

from app.family.services import FamilyService
from app.services.service_base import service_response
from app.utils.constants import Gender
from tests.utils import login_test_user_1


def test_index(client, test_user_1):
    """
    Tests the 'index' view of the 'family' blueprint to ensure it renders
    correctly and contains expected content.

    Args:
    client: Flask test client used to simulate HTTP requests during testing.
    test_user_1: Fixture providing a test user object.

    Raises:
    AssertionError: If the response status code is not 200 or expected content
    is not found in the response data.
    """
    login_test_user_1(client, test_user_1)

    response = client.get(url_for("family.index"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Create Family" in response.data

def test_index_with_family_id(client, test_user_and_family):
    """
    Executes a test case to verify that the 'index' page for a specific family ID renders
    successfully after authenticating the test user.

    Parameters:
    client : flask.testing.FlaskClient
        A test client object for simulating requests to the application.
    test_user_and_family : tuple
        A tuple containing a test user and their associated family.

    Raises:
    AssertionError
        If the response status code is not 200 or if the expected content is not in the
        response data.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.get(url_for("family.index", family_id=family.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Family 1" in response.data

def test_index_with_invalid_family_id(client, test_user_and_family, test_family_2):
    """
    Tests the accessibility of the family index page with an invalid family ID to
    ensure the system properly handles unauthorized access by redirecting the user
    and displaying an appropriate error message.

    Args:
        client: Flask test client used to simulate HTTP requests in testing.
        test_user_and_family: Tuple containing a user object and their associated
            family object.
        test_family_2: A second family object used for testing unauthorized access.

    Raises:
        AssertionError: If the response status code is not 200, or the error message
        does not appear in the response data.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)
    response = client.get(url_for("family.index", family_id=test_family_2.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this family" in response.data

def test_create_family_get(client, test_user_1):
    """
    Test the GET request for the 'create_family' route to verify that it renders
    the intended page content and returns the appropriate HTTP response code.

    Parameters:
    client: flask.testing.FlaskClient
        A test client used to simulate requests to the Flask application.
    test_user_1: User
        A user used for authentication in the test.

    This test ensures the following:
    - The 'create_family' route renders successfully without errors.
    - The HTTP status code returned is 200 (OK).
    - The page contains the expected content, such as "Create Family".
    """
    login_test_user_1(client, test_user_1)
    response = client.get(url_for("family.create_family"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Create Family" in response.data

def test_create_family_post(client, test_user_1):
    """
    Tests the creation of a new family and its root member using the provided client and test user.

    This function performs the following steps:
    1. Logs in the test user.
    2. Defines forms for creating a family and a root family member.
    3. Sends a POST request to the family creation route with the provided data.
    4. Asserts that the response status is successful and required elements are
       present in the response.

    Parameters:
        client: The testing client is used to simulate requests to the application.
        test_user_1: The user object used for authentication during the test.

    Raises:
        AssertionError: If any of the assertions regarding the response status or
                        content fail.
    """
    login_test_user_1(client, test_user_1)
    family_form = {"name": "Test family"}
    member_form = {"first_name": "test_first_name",
                   "last_name": "test_last_name",
                   "birthdate": datetime(2023, 1, 1).strftime("%Y-%m-%d"),
                   "gender": Gender.MALE.value,
                   "alive": True,}
    response = client.post(
        url_for("family.create_family"),
        data=dict(**family_form, **member_form),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Root member created successfully" in response.data
    assert b"Family created successfully" in response.data
    assert b"Test family" in response.data
    assert b"test_first_name" in response.data

def test_create_family_post_error_creating_family(client, test_user_1, monkeypatch):
    """
    Test case for ensuring the proper handling of an error during the creation of
    a family using the FamilyService. This function tests the scenario where the
    service call to create a family returns an HTTP 500 status code.

    Parameters:
    client : flask.testing.FlaskClient
        The test client to simulate requests to the Flask application.
    test_user_1 : User
        A fixture that provides a test user object for authentication.
    monkeypatch : pytest.MonkeyPatch
        Pytest utility to dynamically replace attributes and behaviors during the
        test.

    Test behavior includes:
    - Simulating user login to authenticate the request.
    - Patching the `create_family` method in the `FamilyService` to return a
      mocked error response with an HTTP 500 status code.
    - Sending a POST request to the `create_family` endpoint with the family and
      member data.
    - Asserting that the response has HTTP status 200 to verify proper error
      display handling on the frontend.
    - Verifying specific error messages and UI components in the response.
    """
    login_test_user_1(client, test_user_1)

    def mock_create_family(*args, **kwargs):
        return service_response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Error creating family",
            "danger",
            None
        )
    monkeypatch.setattr(FamilyService, "create_family", mock_create_family)

    family_form = {"name": "Test family"}
    member_form = {"first_name": "test_first_name",
                   "last_name": "test_last_name",
                   "birthdate": datetime(2023, 1, 1).strftime("%Y-%m-%d"),
                   "gender": Gender.MALE.value,
                   "alive": True,}
    response = client.post(
        url_for("family.create_family"),
        data=dict(**family_form, **member_form),
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Error creating family" in response.data
    assert b"Create Family" in response.data
    assert b"Test family" not in response.data
    assert b"test_first_name" not in response.data

def test_delete_family(client, test_user_and_family):
    """
    Tests the deletion of a family record associated with a user in a web application.

    This test verifies that after a successful deletion operation, the family record no
    longer appears in the response and an appropriate confirmation message is displayed.

    Parameters:
    client: FlaskClient
        A test client representing the Flask application for simulating HTTP requests.
    test_user_and_family: tuple[User, Family]
        A test fixture providing a user instance and associated test family instance.

    Raises:
    AssertionError
        If the response status code is not 200, if the success message is not included
        in the response data, or if the deleted family name still exists in the response.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("family.delete_family", family_id=family.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"Family deleted successfully" in response.data
    assert b"Test Family 1" not in response.data

def test_delete_family_error(client, test_user_and_family, test_family_2):
    """
    Tests the scenario where a user attempts to delete a family they are not authorized to delete.

    This test ensures the application correctly prevents users from deleting families they do not
    own and provides an appropriate response to inform the user of the action restriction.

    Args:
        client: A test client instance used to send requests to the application during the test.
        test_user_and_family: A fixture providing a test user and an associated family for the
            purpose of validating user actions.
        test_family_2: A fixture providing a second family object unrelated to the primary test
            user to evaluate access restrictions.

    Raises:
        AssertionError: If the response status code is not 200, or if the expected error message
            is not found in the response data.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("family.delete_family", family_id=test_family_2.family_id), follow_redirects=True)
    assert response.status_code == 200
    assert b"You are not allowed to delete this family" in response.data