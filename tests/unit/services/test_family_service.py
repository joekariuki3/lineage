from app.family.services import FamilyService
from app.models import Family


def test_get_family_by_id(test_family_1):
    """
    Tests the `get_family_by_id` method from the `FamilyService` class. Ensures
    that the method correctly retrieves a family record by its unique identifier
    and validates the returned response and status code.

    Parameters:
    test_family_1 : Family
        A test fixture or mocked object representing a family entity, which includes
        the family ID that will be used for querying.

    Raises:
    AssertionError
        If the status code does not match 200, or the response message and data values
        do not match the expected results.
    """
    service = FamilyService()
    response, status = service.get_family_by_id(test_family_1.family_id)
    assert status == 200
    assert response['message'] == "Family found"
    assert response['data'] == test_family_1

def test_get_family_by_id_nonexistent(app):
    """
    Test function for checking the behavior of the get_family_by_id method
    when a family with a nonexistent ID is requested. This test ensures that
    the function returns the correct status and error message for invalid
    input.

    Parameters:
        app: Flask app instance used for testing.
    """
    service = FamilyService()
    response, status = service.get_family_by_id(17)
    assert status == 404
    assert response['message'] == "Family not found"
    assert response['data'] is None

def test_get_family_by_id_error(test_family_1, monkeypatch):
    """
    Tests the behavior of the `get_family_by_id` method in `FamilyService` when a database error occurs.
    The database query method is mocked to raise an exception, simulating a database failure.

    Args:
        test_family_1: Fixture representing a mocked family object or test data
            used in testing.
        monkeypatch: Fixture provided by pytest, used to modify or override
            objects and functions during testing.
    """
    service = FamilyService()

    def mock_query(*args):
        raise Exception("Database error")
    monkeypatch.setattr(service.db, "query", mock_query)
    _, status = service.get_family_by_id(family_id=test_family_1.family_id)
    assert status == 500

def test_get_user_families(test_user_with_two_families):
    """
    Test the retrieval of user families using the FamilyService class.

    This function checks if the `get_user_families` method of the FamilyService
    class works as expected. It validates that the correct status code, message,
    and family data are returned when a user with two families is provided.

    Parameters
    ----------
    test_user_with_two_families : User
        a user that is associated with twp families
    """
    service = FamilyService()
    response, status = service.get_user_families(test_user_with_two_families.user_id)
    assert status == 200
    assert response['message'] == "Families found"
    assert len(response['data']) == 2

def test_get_user_families_no_families(test_user_1):
    """
    Tests the retrieval of user families when no families exist for the given user.

    This test ensures that the get_user_families method of FamilyService
    returns the correct response and status code when no families are found
    for the user ID provided.

    Args:
        test_user_1 (User): A test user object used to perform the test.

    Raises:
        AssertionError: If the response status code or message does not match
        the expected outcome.
    """
    service = FamilyService()
    response, status = service.get_user_families(test_user_1.user_id)
    assert status == 404
    assert response['message'] == "No families found"
    assert response['data'] is None

def test_get_user_families_error(test_user_with_two_families, monkeypatch):
    """
    Test function for handling errors in the `get_user_families` method of the
    `FamilyService` when a database query fails. It simulates a scenario where
    an exception is raised during a database operation and ensures that the
    method handles the error correctly.

    Parameters
    ----------
    test_user_with_two_families : User
        A fixture object representing a test user associated with
        two family records in the database.

    monkeypatch : pytest.MonkeyPatch
        A fixture provided by pytest to modify or replace the behavior of
        objects or methods during testing.

    Raises
    ------
    Exception
        Raised during the database query to simulate an error condition.
    """
    service = FamilyService()

    def mock_query(*args):
        raise Exception("Database error")
    # mock the database query method to raise an exception during the family retrieval
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_user_families(test_user_with_two_families.user_id)
    assert status == 500
    assert response['message'] == "Error retrieving families"
    assert response['data'] is None

def test_create_family(app):
    """
    Tests the creation of a family using the FamilyService.

    Provides assertions to validate the successful execution of the create_family
    method, verifying that the expected status code, message, and family name
    are correctly returned.

    Parameters:
        app: Flask app instance used for testing.

    Raises:
        AssertionError: If any of the assertions fail, indicating unexpected
                        behavior in the family creation process.
    """
    service = FamilyService()
    response, status = service.create_family(family_name="new_family", user_id=1)
    assert status == 201
    assert response['message'] == "Family created successfully"
    assert response['data'].name == "new_family"

def test_create_family_error(app, monkeypatch):
    """
    Tests the behavior of the `create_family` method in the `FamilyService`
    class when the database add operation fails due to an exception.

    This test simulates a failure in the database add operation to verify
    that the service correctly handles the exception and returns the
    appropriate response and status code.

    Parameters
    ----------
    app: Flask app instance used for testing.
    monkeypatch : pytest.MonkeyPatch
        A fixture provided by pytest to modify or replace the behavior of
        objects or methods during testing.
    """
    service = FamilyService()

    def mock_add(*args):
        raise Exception("Database error")

    # mock the database add method to raise an exception during the family creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_family(family_name="new_family", user_id=1)
    assert status == 500
    assert response['message'] == "Error creating family"
    assert response['data'] is None

def test_family_belongs_to_user(test_user_with_one_family):
    """
    Tests if a family belongs to a specified user.

    This function verifies whether the family associated with the given
    user ID belongs to the user by utilizing the FamilyService class.
    This is achieved by comparing the user ID and family ID within
    the test setup.

    Args:
        test_user_with_one_family: An instance representing a test user
            with exactly one associated family. The `user_id` identifies
            the user, and `families` is a list containing one family with
            its respective `family_id` value.

    """
    service = FamilyService()
    assert service.family_belongs_to_user(test_user_with_one_family.user_id, test_user_with_one_family.families[0].family_id)

def test_family_belongs_to_user_false(test_user_1, test_family_1):
    """
    Tests the `family_belongs_to_user` method to assert that it returns False when
    the specified family does not belong to the given user.

    Arguments:
    test_user_1: User
        The test user with a user_id to verify ownership of the family.
    test_family_1: Family
        The test family object with a family_id that should not belong to the user.

    Raises:
    AssertionError
        If the `family_belongs_to_user` method does not return False when the
        family does not belong to the specified user.
    """
    service = FamilyService()
    assert not service.family_belongs_to_user(test_user_1.user_id, test_family_1.family_id)

def test_delete_family(session):
    """
    Test the deletion of a family record using the FamilyService class.

    This test ensures that a family can be created, committed to the session, and then
    successfully deleted using the delete_family method. It also checks that the response
    message and status code are correct, and verifies that no additional data is returned
    in the response.

    Parameters:
    session: Session
        The database session used for creating and committing the family record.

    Raises:
    AssertionError
        If any of the response values (status, message, or data) do not match the
        expected outcome.
    """
    family = Family(name="Test Family", user_id=1)
    session.add(family)
    session.commit()

    service = FamilyService()
    response, status = service.delete_family(family.family_id)
    assert status == 200
    assert response['message'] == "Family deleted successfully"
    assert response['data'] is None

def test_delete_non_existing_family(app):
    """
    Test the deletion of a non-existing family and response handling in the FamilyService.

    The function tests the `delete_family` method by attempting to delete a
    family that is known to not exist, verifying that the response and status
    returned are correct.

    Parameters:
        app: Flask app instance used for testing.
    """
    service = FamilyService()
    response, status = service.delete_family(17)
    assert status == 404
    assert response['message'] == "Family not found"

def test_delete_family_error(session, monkeypatch):
    """
    Test the deletion of a family entity when a database error occurs during the
    process.

    Arguments:
        session (Session): The database session used for setting up and
            committing test data before the test execution.
        monkeypatch (MonkeyPatch): A pytest fixture that is used for
            dynamically modifying classes or objects during testing.

    Raises:
        Exception: Mocked exception that simulates a database error during
            the deletion of a family entity.
    """
    family = Family(name="Test Family", user_id=1)
    session.add(family)
    session.commit()

    service = FamilyService()

    def mock_delete(*args):
        raise Exception("Database error")

    # mock the database delete method to raise an exception during the family deletion
    monkeypatch.setattr(service.db, "delete", mock_delete)

    response, status = service.delete_family(family.family_id)
    assert status == 500
    assert response['message'] == "Error deleting family"
    assert response['data'] is None