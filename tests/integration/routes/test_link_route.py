from flask import url_for

from tests.utils import login_test_user_1


def test_create_link(client, test_user_and_family):
    """
    Tests the functionality for creating a family link using the provided client and test data.

    This test ensures that a user can successfully create a link associated with their family
    after logging in. It verifies the HTTP response status code and checks for the expected
    success message in the response data.

    Parameters:
        client
            A test client instance used to simulate requests to the application server.
        test_user_and_family
            A tuple containing a test user object and their associated family object.
    """
    user, family = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("link.create_link"), data={"family_id": family.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link created successfully" in response.data

    # create a link a second time when a link already exists
    response = client.post(url_for("link.create_link"), data={"family_id": family.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link already exists for this family" in response.data

def test_create_link_no_family_id(client, test_user_1):
    """
    Tests the creation of a link without providing a family id. Ensures proper handling
    of missing required data by the request handler and validates the returned
    response and error message to confirm expected application behavior.

    Args:
        client: Flask test client used to simulate and make requests to
            the application during testing.
        test_user_1: Predefined test user fixture provided for authentication
            purposes during tests.

    Raises:
        AssertionError: If the response status code is not 200, or the expected
            error message is not found in the response data.
    """
    login_test_user_1(client, test_user_1)
    response = client.post(url_for("link.create_link"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Family id is required" in response.data

def test_create_link_non_existing_family(client, test_user_1):
    """
    Tests the creation of a link with a non-existing family ID to ensure that
    the server responds appropriately by indicating the family was not found.

    Args:
    client: The test client is used to mock HTTP requests.
    test_user_1: A test user object used for login authentication.

    Raises:
    AssertionError: If the HTTP status code is not 200 or if the response
    does not contain the expected message indicating the family was not found.
    """
    login_test_user_1(client, test_user_1)
    response = client.post(url_for("link.create_link"), data={"family_id": 100}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Family not found" in response.data

def test_create_link_for_family_not_belonging_to_user(client, test_user_and_family, test_family_2):
    """
    Tests the creation of a family link for a family not belonging to the user.
    Ensures that users cannot create links for unauthorized families.

    Args:
        client: Test client for making HTTP requests.
        test_user_and_family: Fixture providing a test user and associated family.
        test_family_2: Fixture providing a second test family not associated with the test user.

    Raises:
        AssertionError: If the response status code is not 200 or if the error message
        "You do not have permission to access this family" is not found in the response.
    """
    user, _ = test_user_and_family
    login_test_user_1(client, user)
    response = client.post(url_for("link.create_link"), data={"family_id": test_family_2.family_id}, follow_redirects=True)
    assert response.status_code == 200
    assert b"You do not have permission to access this family" in response.data

def test_delete_link(client, test_user_and_family, test_link_1):
    """
    Tests the functionality of deleting a link associated with a family.

    The function ensures the link deletion process is successfully implemented,
    handles successive deletion requests correctly, and verifies appropriate
    application behavior when attempting to delete a non-existent link.

    Parameters:
    client : FlaskClient
        The test client for simulating requests to the Flask application.
    test_user_and_family : tuple
        A tuple containing a test user object and an associated family object.
        Used for user authentication and linking data setup.
    test_link_1 : Link
        A test link object that becomes associated with a specific family and
        subsequently tested for deletion.

    Raises:
    AssertionError
        If any condition in the test fails, such as unexpected HTTP response
        status codes or unexpected response data.
    """
    user, family = test_user_and_family
    # associate link with family
    test_link_1.family_id = family.family_id

    login_test_user_1(client, user)

    data = {"link_id": test_link_1.link_id, "family_id": family.family_id,}
    response = client.post(url_for("link.delete_link"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link deleted successfully" in response.data

    # delete the link again to make sure the appropriate action realized
    response = client.post(url_for("link.delete_link"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link not found" in response.data

def test_delete_link_no_link_id(client, test_user_and_family, test_link_1):
    """
    Tests the scenario where a request to delete a link is made without providing a link ID.

    This test checks the behavior of the link deletion endpoint when the 'link_id' parameter
    is not included in the provided data. It ensures that the application returns the
    appropriate response and does not process the deletion.

    Args:
        client: Flask test client to simulate requests to the application.
        test_user_and_family: Tuple containing a mock user and associated family for
            testing.
        test_link_1: A mock link object associated with a family for the purpose of the test.

    Raises:
        AssertionError: If the response does not meet the expected conditions.
    """
    user, family = test_user_and_family
    # associate link with family
    test_link_1.family_id = family.family_id

    login_test_user_1(client, user)

    data = {"family_id": family.family_id, }
    response = client.post(url_for("link.delete_link"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Link id is required" in response.data

def test_delete_link_no_family_id(client, test_user_and_family, test_link_1):
    """
    Tests the behavior of deleting a link without providing a family ID.

    This function simulates an attempt to delete a link while omitting the required
    family ID in the provided data. It verifies that the application properly handles
    this scenario by checking the response status and the error message shown.

    Parameters:
    client
        The test client used to simulate HTTP requests to the application.
    test_user_and_family
        A tuple containing a test user and the associated family used for testing.
        Each entry corresponds to the test user and their family details.
    test_link_1
        The test link object that is used for associating it to the family.

    Raises:
    AssertionError
        If the response status code does not match 200 or if the expected error
        message is not found in the response data.
    """
    user, family = test_user_and_family
    # associate link with family
    test_link_1.family_id = family.family_id

    login_test_user_1(client, user)

    data = {"link_id": test_link_1.link_id, }
    response = client.post(url_for("link.delete_link"), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Family id is required" in response.data