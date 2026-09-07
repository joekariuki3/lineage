from http import HTTPStatus

from app.relationship.services import RelationshipService
from app.utils.constants import RelationType


def test_create_relationship_invalid_member(test_member_1):
    """
    Tests the handling of invalid member relationship creation in the RelationshipService class.
    The test ensures that the service responses are correct when one or both members involved
    in a relationship creation request do not exist.

    Args:
        test_member_1 (TestMember): A test fixture providing mock data for a single member.

    Raises:
        AssertionError: If the service does not return the expected HTTP status or response message.
    """
    service = RelationshipService()
    response, status = service.create_relationship(test_member_1.member_id, 17, RelationType.SPOUSE)
    assert status == HTTPStatus.NOT_FOUND
    assert response['message'] == 'One or both members not found'

def test_create_relationship(test_member_1, test_member_2):
    """
    Tests the creation of a relationship between two members using the `RelationshipService` class.

    This function validates that a relationship is successfully created between two given members
    by verifying the HTTP status code and response message returned by the service.

    Args:
        test_member_1 (Member): The first test member involved in the relationship.
        test_member_2 (Member): The second test member involved in the relationship.

    Raises:
        AssertionError: If the relationship creation fails or the response does not match the expected values.
    """
    service = RelationshipService()

    response, status = service.create_relationship(test_member_1.member_id, test_member_2.member_id, RelationType.SPOUSE)
    assert status == HTTPStatus.CREATED
    assert response['message'] == 'Relationship created successfully'

def test_create_relationship_error(test_member_1, test_member_2, monkeypatch):
    """
    This function tests the behavior of the `create_relationship` method of the
    `RelationshipService` class when an error occurs during the relationship creation
    process in the database. The database's add method is mocked to simulate an exception,
    and the test asserts that the error is handled gracefully by returning the correct
    HTTP status code and error message.

    Parameters:
        test_member_1: The first test member object with attributes such as `member_id`.
        test_member_2: The second test member object with attributes such as `member_id`.
        monkeypatch: A pytest fixture for dynamically replacing attributes and methods
            during testing.
    """
    service = RelationshipService()

    def mock_add(*args):
        raise Exception("Database error")

    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_relationship(test_member_1.member_id, test_member_2.member_id, RelationType.SPOUSE)
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response['message'] == 'Error creating relationship'