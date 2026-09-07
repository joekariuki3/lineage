from http import HTTPStatus

from flask_login import login_user
from sqlalchemy.exc import SQLAlchemyError

from app.link.services import LinkService
from app.models import Family, Link


def test_check_existing_link(test_link_1):
    """
    Tests the `_check_existing_link` method of the `LinkService` class.

    This function verifies if the `_check_existing_link` method correctly checks for
    the existence of a link based on the provided family ID.

    Arguments:
        test_link_1 (Link): An instance of `Link` containing data to simulate
            a family link for testing.

    Raises:
        AssertionError: Raised if the `_check_existing_link` method does not behave
            as expected based on the `TestLink` input.
    """
    service = LinkService()
    assert service._check_existing_link(family_id=test_link_1.family_id)

def test_check_existing_link_no_link(app):
    """
    Tests the `_check_existing_link` method of the LinkService class
    to verify that it returns False when no link exists for the given
    family ID.

    Parameters:
        app: Flask app instance.
    """
    service = LinkService()
    assert not service._check_existing_link(family_id=17)

def test_create_link(test_family_1):
    """
    Tests the functionality of the create_link method in the LinkService class for
    creating a new link associated with a family.

    Args:
        test_family_1 (Family): A Family object to which the link is associated.

    Raises:
        AssertionError: If the creation of the link does not return the expected
        status code or response structure.

    """
    service = LinkService()
    response, status = service.create_link(test_family_1)
    assert status == HTTPStatus.CREATED
    assert response["message"] == "Link created successfully"
    assert response["category"] == "success"
    assert response["data"] in test_family_1.links

def test_create_link_for_family_with_existing_link(test_family_with_a_link):
    """
    Tests the behavior of the `create_link` method in `LinkService` when attempting
    to create a link for a family that already has an existing link. Ensures that
    the method returns the appropriate conflict status and message, along with
    no data.

    Parameters:
    test_family_with_a_link: object
        A test fixture representing a family instance that already has an
        associated link.

    Raises:
    AssertionError
        If the status returned by the `create_link` method is not equal to
        `HTTPStatus.CONFLICT`.
        If the response message is not "Link already exists for this family".
        If the response data is not `None`.
    """
    service = LinkService()
    response, status = service.create_link(test_family_with_a_link)
    assert status == HTTPStatus.CONFLICT
    assert response["message"] == "Link already exists for this family"
    assert response["data"] is None

def test_create_link_error(test_family_1, monkeypatch):
    """
    Simulates and tests the behavior of the LinkService when an error occurs during
    creation of a link due to a mocked database issue.

    Parameters:
    test_family_1: dict
        A dictionary representing test family data used to simulate the payload for
        creating a link.
    monkeypatch: pytest.MonkeyPatch
        A fixture for dynamically modifying and testing the behavior of objects,
        methods, or attributes.

    Raises:
    Exception
        An exception is raised during the mocked "add" operation in the database
        to simulate a database error.
    """
    service = LinkService()

    def mock_add(*args):
        raise Exception("Database error")

    # Mock the database add method to simulate an error during link creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_link(test_family_1)
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error creating link"
    assert response["data"] is None

def test_delete_link(session, test_user_1, test_family_1):
    """
    Deletes a link from the database and verifies the operation.

    This function tests the `delete_link` method of the `LinkService` by creating
    a new link associated with a family and user, committing it to the database,
    and then attempting to delete the link through the service. It ensures that the
    link is removed successfully, checks the status code, verifies the response
    message, and ensures no data is returned in the response.

    Parameters:
    session: Database session used to interact with the database.
    test_user_1: A test user instance associated with the family.
    test_family_1: A test family instance associated with the link.

    Raises:
    AssertionError: If the tests on status, response message, or response data fail.
    """
    service = LinkService()
    link = Link(link="https://www.joelmuhoho.com", family_id=test_family_1.family_id)
    session.add(link)
    test_family_1.user_id = test_user_1.user_id
    test_family_1.links.append(link)
    session.commit()

    login_user(test_user_1)

    response, status = service.delete_link(link_id=link.link_id,
                                           family_id=test_family_1.family_id,
                                           user_id=test_user_1.user_id)
    assert status == HTTPStatus.OK
    assert response["message"] == "Link deleted successfully"
    assert response["data"] is None
    assert status == HTTPStatus.OK
    assert response["message"] == "Link deleted successfully"
    assert response["data"] is None

def test_delete_link_unauthorized_user(test_user_1, test_family_1, test_link_1):
    """
    Tests the scenario where an unauthorized user attempts to delete a link. This ensures that the
    system enforces authorization policies and does not permit unauthorized deletions.

    Args:
        test_user_1: Mock user object representing the unauthorized user.
        test_family_1: Mock family object associated with the user's request.
        test_link_1: Mock link object representing the link intended to be deleted.

    Raises:
        AssertionError: If the deletion status is not HTTPStatus.FORBIDDEN or the response
        contains unexpected data.
    """
    service = LinkService()
    response, status = service.delete_link(link_id=test_link_1.link_id,
                                           user_id=test_user_1.user_id,
                                           family_id=test_family_1.family_id,)
    assert status == HTTPStatus.FORBIDDEN
    assert response["message"] == "You do not have permission to delete this link"
    assert response["data"] is None

def test_delete_link_nonexistent_link(test_user_and_family):
    """
    Test the deletion of a nonexistent link for a user within a family.

    This function validates the behavior of attempting to delete a link
    that does not exist for a specific user and family. The test ensures
    that the system correctly identifies the missing link and returns the
    appropriate response and status code.

    Args:
        test_user_and_family: tuple
            A fixture providing a test user and their associated family object.

    Raises:
        AssertionError: If the status returned is not HTTPStatus.NOT_FOUND or the
        message in the response is not "Link not found".
    """
    user, family = test_user_and_family
    # log in the user in order for them to perform the deletion
    login_user(user)

    service = LinkService()
    response, status = service.delete_link(link_id=17, family_id=family.family_id, user_id=user.user_id)
    assert status == HTTPStatus.NOT_FOUND
    assert response["message"] == "Link not found"

def test_delete_link_database_sqlalchemy_error(session, test_user_1, monkeypatch):
    """
    Test case for simulating an SQLAlchemy error during the deletion of a link.

    This test validates the error handling mechanism of the `delete_link` service
    method when a database-level exception occurs. It mocks the database deletion
    operation to simulate the error and ensures the service responds appropriately.

    Parameters:
        session: Session
            The database session fixture for committing and managing transaction
            states during the test.
        test_user_1: A user object representing the authenticated user attempting the action.
        monkeypatch: MonkeyPatch
            The mock fixture for replacing components or functions with test-specific
            implementations.

    Raises:
        SQLAlchemyError: Mocked error to simulate a database issue during the delete
        operation.
    """
    # associate the link with the family and current_user (test_user_1)
    family = Family(name="family_1", user_id=test_user_1.user_id)
    family.user_id = test_user_1.user_id
    session.add(family)
    session.commit()
    link = Link(link="https://www.joelmuhoho.com", family_id=family.family_id)
    session.add(link)
    session.commit()

    login_user(test_user_1)

    service = LinkService()

    def mock_delete(*args):
        raise SQLAlchemyError("Database error")

    # Mock the database delete method to simulate a sqlalchemy error during link deletion
    monkeypatch.setattr(service.db, "delete", mock_delete)

    response, status = service.delete_link(link_id=link.link_id,
                                           family_id=family.family_id,
                                           user_id=test_user_1.user_id, )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Database error occurred while deleting link"
    assert response["data"] is None

    monkeypatch.undo()

def test_delete_link_error(session, test_user_1, monkeypatch):
    """
    Tests the behavior of the `delete_link` method in `LinkService` when an exception is raised during
    link deletion.

    The test ensures that the method handles unexpected database errors gracefully by returning an
    appropriate response and HTTP status code.

    Args:
        session: A fixture that provides a database session for setting up the testing
            environment.
        test_user_1: A user object representing the authenticated user attempting the action.
        monkeypatch: A fixture that allows overriding attributes, methods, or functions during testing.

    Raises:
        Exception: Simulates a database error raised during the deletion of the link.
    """
    service = LinkService()

    # associate the link with the family and current_user (test_user_1)
    family = Family(name="family_1", user_id=test_user_1.user_id)
    family.user_id = test_user_1.user_id
    session.add(family)
    session.commit()
    link = Link(link="https://www.joelmuhoho.com", family_id=family.family_id)
    session.add(link)
    session.commit()

    login_user(test_user_1)

    def mock_delete(*args):
        raise Exception("Database error")

    # Mock the database delete method to simulate an exception error during link deletion
    monkeypatch.setattr(service.db, "delete", mock_delete)

    response, status = service.delete_link(link_id=link.link_id,
                                           family_id=family.family_id,
                                           user_id=test_user_1.user_id, )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Unexpected error while deleting link"
    assert response["data"] is None

    monkeypatch.undo()