from http import HTTPStatus

from flask_login import login_user, logout_user

from app.member.services import MemberService
from app.models import Family, Member, Relationship
from app.utils.constants import Gender, RelationType


def test_get_member_unauthenticated(test_member_1):
    """
    Tests the behavior of the get_member method when the user is unauthenticated.

    This test ensures that the service correctly handles unauthenticated access and
    returns the appropriate HTTP status code and response when attempting to retrieve
    a member's information without being logged in.

    Attributes:
        test_member_1 (Member): A pre-created test instance of the Member model
            with a valid member_id used for testing.

    Parameters:
        test_member_1 (Member): The member instance to test retrieving member
            information when unauthenticated.

    Returns:
        None
    """
    logout_user()
    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)
    assert status == HTTPStatus.UNAUTHORIZED
    assert response["data"] is None


def test_get_member_not_found(test_user_1):
    """
    Tests the retrieval of a member that does not exist in the system.

    The function simulates a situation where the user is logged in, and an attempt is made
    to retrieve a member with an ID that does not exist, ensuring the system correctly
    returns a NOT_FOUND status and no member data.

    Args:
        test_user_1: A test fixture representing a user.

    Raises:
        AssertionError: If the response does not match the expected outcome.
    """
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(9999)

    assert status == HTTPStatus.NOT_FOUND
    assert response["data"] is None


def test_get_member_forbidden(test_member_1, test_user_1):
    """
    Tests the behavior of the MemberService for users attempting to access
    restricted members' data without appropriate permissions.

    This test confirms that an authenticated user cannot access
    the data of a member they are unauthorized to view,
    and that the appropriate HTTP status and response are returned.

    Args:
        test_member_1: A test member object that the user attempts
                       to access.
        test_user_1: A test user object representing the user
                     performing the access.

    Raises:
        AssertionError: If the returned HTTP status code or response
                        data does not meet the expected conditions.
    """
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)
    assert status == HTTPStatus.FORBIDDEN
    assert response["data"] is None


def test_get_member_success(session, test_member_1, test_user_1):
    """
    Tests the successful retrieval of a member's information.

    This function verifies that a member's data can be successfully retrieved
    when the member is associated with a family, and the user has access to
    the respective family.

    Parameters:
    session : Session object
        The database session used for committing changes and verifying the test.
    test_member_1 : Member object
        The test member whose data is to be retrieved.
    test_user_1 : User object
        The test user attempting to access the member's data.

    Raises:
    AssertionError
        If the response status is not HTTPStatus.OK or if the retrieved data
        does not match the `test_member_1` information.
    """
    family = test_member_1.family
    test_user_1.families.append(family)
    session.commit()
    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member(test_member_1.member_id)

    assert status == HTTPStatus.OK
    assert response["data"] == test_member_1


def test_get_member_error(session, test_member_1, test_user_1, monkeypatch):
    """
    Simulates an error during the retrieval of a family member's details by mocking the query
    method in the service layer. Verifies that the application handles the error as expected
    and returns the appropriate HTTP status and response structure.

    Args:
        session: Database session configured for the test.
        test_member_1: Test fixture representing a sample member of a family.
        test_user_1: Test fixture representing a sample user.
        monkeypatch: Fixture used to dynamically replace the behavior of objects.

    Raises:
        Exception: Mocked query function raises an exception to simulate a database error.

    Returns:
        None
    """
    family = test_member_1.family
    test_user_1.families.append(family)
    session.commit()
    login_user(test_user_1)

    service = MemberService()

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during member retrieval
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member(test_member_1.member_id)

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["data"] is None


def test_is_member_accessible_by_user_true(test_member_1, test_user_1):
    """
    Checks if a specific member is accessible by a user through the member's
    associated family. The function ensures the user is logged in, associates
    the member's family with the user, and then verifies accessibility using
    the MemberService class.

    Args:
        test_member_1: The member whose accessibility will be checked by the user.
        test_user_1: The user for whom member accessibility is validated.

    Raises:
        AssertionError: If the member is not accessible by the user as expected.
    """
    login_user(test_user_1)

    # associate the member family with the user
    family = test_member_1.family
    test_user_1.families.append(family)

    service = MemberService()

    assert service.is_member_accessible_by_user(test_member_1)


def test_is_member_accessible_by_user_false(test_member_1, test_user_1):
    """
    Determines if a member is accessible by a specific user and asserts that it is not.

    Tests the `is_member_accessible_by_user` method provided by `MemberService` to
    ensure that the given member is not accessible to the provided user after logging
    into the system with the user.

    Parameters:
    test_member_1: The member object to test accessibility for.
    test_user_1: The user object to test access rights against.
    """
    login_user(test_user_1)

    service = MemberService()
    assert not service.is_member_accessible_by_user(test_member_1)


def test_create_member(app):
    """
    Tests the `create_member` functionality of the `MemberService` class to ensure
    a member is successfully created given valid input parameters. Verifies that
    the response includes the expected message, category, and data, and that the
    HTTP status code matches the expected value.

    Args:
        app: Flask application instance used for setting up the test environment.

    Raises:
        AssertionError: If the response message, category, data, or status code
        does not match the expected output.
    """
    service = MemberService()

    response, status = service.create_member(
        first_name="Allan", last_name="Kim", family_id=1, gender=Gender.MALE.value
    )

    assert status == HTTPStatus.CREATED
    assert response["message"] == "Member created successfully"
    assert response["category"] == "success"
    assert response["data"] is not None


def test_create_member_error(app, monkeypatch):
    """
    Tests the behavior of the `create_member` method within the `MemberService` class
    when an exception is raised during the database `add` operation.

    This function mocks the `db.add` method to simulate a database error, invokes the
    `create_member` method, and asserts that the correct response and status code
    are returned when a failure occurs during member creation.

    Parameters
    ----------
    app : Any
        The application instance to be passed into the test context, if used.
    monkeypatch : MonkeyPatch
        A pytest fixture used to modify or simulate functionality during testing.

    Raises
    ------
    Exception
        When the mocked `db.add` method is called to simulate a database error.

    Returns
    -------
    None
    """
    service = MemberService()

    def mock_add(*args):
        raise Exception("Database error")

    # mock the database add method to simulate an error during member creation
    monkeypatch.setattr(service.db, "add", mock_add)

    response, status = service.create_member(
        first_name="Allan",
        last_name="Kim",
        family_id=1,
    )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error creating member"
    assert response["data"] is None


def test_get_member_siblings_not_found(session, test_user_1, test_member_1):
    """
    Tests that the `get_member_siblings` method of the `MemberService` returns the
    correct response when no siblings are found for the given member.

    Parameters:
    test_user_1: User
        The mock user object representing the current logged-in user in the test.
    test_member_1: Member
        The mock member object representing the member whose siblings are being
        requested.

    Raises:
    AssertionError
        If the returned status is not HTTPStatus.NOT_FOUND, or if the sibling's
        data in the response is not None.
    """
    # set current_user (test_user_1) to be in the same family as our member
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.NOT_FOUND
    assert response["message"] == "No siblings found"
    assert siblings is None


def test_get_member_siblings(
    session, test_user_1, test_member_1, test_member_2, test_member_3
):
    """
    Tests retrieval of siblings for a given member within the same family. This function verifies that members
    sharing the same father and mother are correctly identified and retrieved as siblings by the service.

    Arguments:
        session: Database session instance used for testing.
        test_user_1: User instance to represent the current logged-in user in the test.
        test_member_1: Member instance for which siblings will be retrieved.
        test_member_2: Member instance representing the first sibling.
        test_member_3: Member instance representing the second sibling.

    Raises:
        AssertionError: If the test conditions for verifying sibling's retrieval are not met.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id

    login_user(test_user_1)
    # associate the members with same father(Member) and mother(Member) id to be siblings
    father_id, mother_id = 20, 30
    test_member_1.father, test_member_1.mother = father_id, mother_id
    test_member_2.father, test_member_2.mother = father_id, mother_id
    test_member_3.father, test_member_3.mother = father_id, mother_id
    session.commit()

    service = MemberService()
    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.OK
    assert len(siblings) == 2
    assert test_member_2 in siblings
    assert test_member_3 in siblings


def test_get_member_siblings_error(
    session, test_user_1, test_member_1, test_member_2, test_member_3, monkeypatch
):
    """
    Tests the behavior of the `get_member_siblings` method of the `MemberService` class
    when the database query for retrieving siblings raises an exception. This test ensures
    that the service properly handles errors during sibling retrieval and returns the
    appropriate response and status code.

    Args:
        session: The database session object used to manage changes and commits during
            testing.
        test_user_1: A predefined test user object that serves as the current logged-in
            user for the duration of the test.
        test_member_1: A predefined test member object whose siblings are to be retrieved
            in the test.
        test_member_2: A predefined test member object representing a sibling of
            `test_member_1`.
        test_member_3: A predefined test member object representing another sibling of
            `test_member_1`.
        monkeypatch: A pytest fixture that allows dynamic modification of attribute
            behavior to mock external dependencies.

    Raises:
        Exception: Simulates a database error during the siblings retrieval process.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id

    login_user(test_user_1)
    # associate the members with same father(Member) and mother(Member) id to be siblings
    father_id, mother_id = 20, 30
    test_member_1.father, test_member_1.mother = father_id, mother_id
    test_member_2.father, test_member_2.mother = father_id, mother_id
    test_member_3.father, test_member_3.mother = father_id, mother_id
    session.commit()

    service = MemberService()

    def mock_get_member(*args):
        """simulates the get_member method of the MemberService class"""
        status = HTTPStatus.OK
        data = test_member_1
        return data, status

    # mock the get_member method to simulate a successful retrieval of a member (test_member_1)
    monkeypatch.setattr(service, "get_member", mock_get_member)

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during siblings retrieval from the database
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member_siblings(test_member_1.member_id)
    siblings = response["data"]
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error retrieving siblings"
    assert siblings is None


def test_get_member_children_not_found(session, test_user_1, test_member_1):
    """
    Tests the `get_member_children` method when no children are found.

    This test ensures that the `get_member_children` method correctly handles the
    scenario where a member has no children and returns the appropriate HTTP status
    and message.

    Parameters
    ----------
    session : Session
        The current database session used for the test.
    test_user_1 : User
        A user object used to simulate the logged-in user.
    test_member_1 : Member
        A member object associated with the test user's family.

    Notes
    -----
    The test associates the logged-in user with the specified member's family,
    then invokes the service method to retrieve children for the member. It verifies
    that the method returns an HTTPStatus.NOT_FOUND response and a message
    indicating no children were found.
    """
    # associate current_user(test_user_1) with test_member_1's family
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member_children(test_member_1.member_id)
    children = response["data"]
    assert status == HTTPStatus.OK
    assert response["message"] == "No children found"
    assert len(children) == 0


def test_get_member_children(
    session, test_user_1, test_member_1, test_member_2, test_member_3
):
    """
    Tests retrieving the children of a specific member through the member service.

    The function prepares the test environment by associating a user and family
    members appropriately, logs in the user, and verifies that the member service
    correctly identifies and returns the children associated with a specific
    member.

    Parameters:
    session : Session
        The database session used to interact with the database during the test.
    test_user_1 : User
        The test user who is set as the current user for the test case.
    test_member_1 : Member
        The member whose children will be fetched during the test.
    test_member_2 : Member
        A member who will be set as a child of test_member_1 for the test case.
    test_member_3 : Member
        Another member who will be set as a child of test_member_1 for the
        test case.

    Raises:
    AssertionError
        If the retrieved children do not match the expected values, or the
        response status is not HTTPStatus.OK.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    # associate test_member_2 and test_member_3 with test_member_1 as their father for them to be children of test_member_1
    test_member_2.father = test_member_1.member_id
    test_member_3.father = test_member_1.member_id
    session.commit()

    service = MemberService()
    response, status = service.get_member_children(test_member_1.member_id)
    children = response["data"]
    assert status == HTTPStatus.OK
    assert len(children) == 2
    assert test_member_2 in children
    assert test_member_3 in children


def test_get_member_children_error(
    session, test_user_1, test_member_1, test_member_2, test_member_3, monkeypatch
):
    """
    Tests the behavior of the `get_member_children` function in the face of a simulated database error during the
    retrieval of children of a specific family member.

    The test:
    - Sets up the test environment by associating a user and their family members.
    - Mocks the `get_member` method of the `MemberService` class to simulate a successful member retrieval.
    - Mocks the `query` method of the database service to simulate a database error on children retrieval.

    This test verifies that the `get_member_children` function correctly handles and responds with an appropriate
    status and data when a database error occurs.

    Args:
        session: The database session fixture for committing test setup data.
        test_user_1: A mocked user fixture to act as the current user.
        test_member_1: A fixture representing the target family member.
        test_member_2: A fixture representing a family member who is a child of test_member_1.
        test_member_3: A fixture representing another child of test_member_1.
        monkeypatch: The pytest monkeypatch fixture for mocking object attributes.

    Raises:
        Exception: Simulates an error during children retrieval from the database.

    Returns:
        None
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    # associate test_member_2 and test_member_3 with test_member_1 as their father for them to be children of test_member_1
    test_member_2.father = test_member_1.member_id
    test_member_3.father = test_member_1.member_id
    session.commit()

    service = MemberService()

    def mock_get_member(*args):
        """simulates the get_member method of the MemberService class"""
        status = HTTPStatus.OK
        data = test_member_1
        return data, status

    # mock the get_member method to simulate a successful retrieval of a member (test_member_1)
    monkeypatch.setattr(service, "get_member", mock_get_member)

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during children retrieval from the database
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member_children(test_member_1.member_id)
    children = response["data"]
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error retrieving children"
    assert children is None


def test_get_member_spouses_not_found(session, test_user_1, test_member_1):
    """
    Test for the get_member_spouses method when no spouses are found.

    This test case ensures that when the service is queried for a member's
    spouses but no spouses exist for the given member, the response
    is properly crafted with an HTTP status of NOT_FOUND and an appropriate
    message. It also verifies that the data for spouses is returned as None.

    Parameters:
        session: The database session fixture used for setting up and rolling
            back test data during the test execution.
        test_user_1: The user fixture representing the currently authenticated
            user in the test case.
        test_member_1: The member fixture representing the member whose
            spouses are being queried in the test case.

    Raises:
        AssertionError: If the expected results including the status, message,
        or spouses data do not match, the test will fail to assert the behavior
        of get_member_spouses method.
    """
    # associate current_user(test_user_1) with test_member_1's family
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    response, status = service.get_member_spouses(test_member_1.member_id)
    spouses = response["data"]
    assert status == HTTPStatus.NOT_FOUND
    assert response["message"] == "No spouses found"
    assert spouses is None


def test_get_member_spouses(session, test_user_1, test_member_1, test_member_2):
    """
    Test the functionality of retrieving spouses for a given family member.

    This test ensures that the `get_member_spouses` method successfully retrieves
    the spouses associated with a specific member of a family. It validates the
    response message, status code, and checks that the correct spouse is present
    in the result.

    Parameters:
    session : Session
        The database session used for committing entities and handling transactions.
    test_user_1 : User
        The test user who will be set as part of the same family as the test members.
    test_member_1 : Member
        The first test family member whose spouses will be retrieved.
    test_member_2 : Member
        The second test family member to be associated as a spouse of the first member.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    # associate test_member_2 as the spouse of test_member_1
    relationship = Relationship(
        member_id_1=test_member_1.member_id,
        member_id_2=test_member_2.member_id,
        relationship_type=RelationType.SPOUSE,
    )
    session.add(relationship)
    session.commit()

    service = MemberService()
    response, status = service.get_member_spouses(test_member_1.member_id)
    spouses = response["data"]
    assert status == HTTPStatus.OK
    assert response["message"] == "Spouses retrieved successfully"
    assert test_member_2 in spouses


def test_get_member_spouses_error(
    session, test_user_1, test_member_1, test_member_2, monkeypatch
):
    """
    Tests the error handling of the `get_member_spouses` method when a database error occurs
    during the retrieval of a member's spouses. Ensures that appropriate error status and
    message are returned, and no spouse data is retrieved.

    Args:
        session (SQLAlchemy Session): A database session for handling database commits and queries.
        test_user_1 (User): A mock user object representing a test user.
        test_member_1 (Member): The primary mock member object for the test.
        test_member_2 (Member): The mock member object to be associated as a spouse.
        monkeypatch (pytest MonkeyPatch): A utility to temporarily replace or mock certain
            attributes or methods during testing.
    """
    # set current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    # associate test_member_2 as the spouse of test_member_1
    relationship = Relationship(
        member_id_1=test_member_1.member_id,
        member_id_2=test_member_2.member_id,
        relationship_type=RelationType.SPOUSE,
    )
    session.add(relationship)
    session.commit()

    service = MemberService()

    def mock_get_member(*args):
        """simulates the get_member method of the MemberService class"""
        status = HTTPStatus.OK
        data = test_member_1
        return data, status

    # mock the get_member method to simulate a successful retrieval of a member (test_member_1)
    monkeypatch.setattr(service, "get_member", mock_get_member)

    def mock_query(*args):
        raise Exception("Database error")

    # mock the query method to simulate an error during spouses retrieval from the database
    monkeypatch.setattr(service.db, "query", mock_query)

    response, status = service.get_member_spouses(test_member_1.member_id)
    spouses = response["data"]
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error retrieving spouses"
    assert spouses is None


def test_update_member(session, test_user_1, test_member_1):
    """
    Tests the update_member functionality in the MemberService class by simulating
    a scenario where a member's details are updated. This test ensures that the
    response contains the updated details and the proper status code is returned.

    Parameters:
        session: Session
            A database session object used to modify the test database context.
        test_user_1: User
            A test user object used to authenticate and represent the current user.
        test_member_1: Member
            A test member object representing a member in the same family
            as the test user.

    Raises:
        AssertionError: If the member update functionality does not produce
            expected results, for instance, incorrect status codes or updated details.

    """
    # assign current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    member_data = {
        "first_name": "New",
        "last_name": "Name",
    }
    response, status = service.update_member(
        member_id=test_member_1.member_id, member_data=member_data
    )

    member = response["data"].member_data
    assert status == HTTPStatus.OK
    assert response["message"] == "Member updated successfully"
    assert member["first_name"] == "New"
    assert member["last_name"] == "Name"


def test_update_member_error(session, test_user_1, test_member_1, monkeypatch):
    """
    Simulates a test case for the `update_member` method in the `MemberService` to handle errors
    that occur during a database commit operation when updating a member's details. It validates
    the service's error-handling capabilities when a database error is raised.

    Arguments:
        session: The database session for performing operations on the test data.
        test_user_1: A user object representing the current logged-in user in the test.
        test_member_1: A member object related to the test scenario.
        monkeypatch: A pytest fixture for dynamically modifying or overriding attributes/methods
            during testing.

    Raises:
        Exception: Simulates a database error during the commit operation.

    """
    # assign current_user (test_user_1) to be in the same family as our members
    test_member_1.family.user_id = test_user_1.user_id
    session.commit()

    login_user(test_user_1)

    service = MemberService()

    def mock_get_member(*args):
        """simulates the get_member method of the MemberService class"""
        status = HTTPStatus.OK
        data = test_member_1
        return data, status

    # mock the get_member method to simulate a successful retrieval of a member (test_member_1)
    monkeypatch.setattr(service, "get_member", mock_get_member)

    def mock_commit(*args):
        raise Exception("Database error")

    # mock the commit method to simulate an error during member update from the database
    monkeypatch.setattr(service.db, "commit", mock_commit)

    member_data = {
        "first_name": "New",
        "last_name": "Name",
    }
    response, status = service.update_member(
        member_id=test_member_1.member_id, member_data=member_data
    )

    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error updating member"
    assert response["data"] is None

    # here we are undoing the monkeypatching to prevent other tests or teardown process using commit from failing
    monkeypatch.undo()


def test_delete_member(session, test_user_1):
    """
    Tests the deletion of a member from a family using the MemberService.

    This function creates a new family and a corresponding member, logs in the test user,
    and uses the MemberService to delete the created member. It ensures that the deletion
    request is successful and validates the response message.

    Parameters:
        session (Session): Database session used for adding and committing test data.
        test_user_1 (User): A test user instance used for authentication and association
        with the family.

    Raises:
        AssertionError: If the deletion operation fails or if the expected status code
        or response message does not match.
    """
    # create a new family and member
    family = Family("new_family", test_user_1.user_id)
    session.add(family)
    session.commit()
    member = Member("new_member", "allan", family.family_id, gender=Gender.MALE.value)
    session.add(member)
    session.commit()

    login_user(test_user_1)

    service = MemberService()
    response, status = service.delete_member(member.member_id)
    assert status == HTTPStatus.OK
    assert response["message"] == "Member deleted successfully"


def test_delete_member_error(session, test_user_1, monkeypatch):
    """
    Tests the behavior of the `delete_member` function in `MemberService` when an exception occurs
    while deleting a member from the database. The test ensures that the appropriate response and
    HTTP status code are returned when an error is encountered during the deletion process.

    Args:
        session: The SQLAlchemy database session used to interact with the database during the test.
        test_user_1: A fixture representing a test user.
        monkeypatch: pytest's monkeypatch utility is used to dynamically alter attributes or methods.

    Raises:
        Exception: Simulated database error triggered during the deletion of a member.
    """
    # create a new family and member
    family = Family("new_family", test_user_1.user_id)
    session.add(family)
    session.commit()
    member = Member("new_member", "allan", family.family_id, Gender.FEMALE.value)
    session.add(member)
    session.commit()

    login_user(test_user_1)

    service = MemberService()

    def mock_delete(*args):
        raise Exception("Database error")

    # mock the delete method to simulate an error during member deletion from the database
    monkeypatch.setattr(service.db, "delete", mock_delete)

    response, status = service.delete_member(member.member_id)
    assert status == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response["message"] == "Error deleting member"
    assert response["data"] is None

    # here we are undoing the monkeypatching to prevent other tests or teardown process using delete from failing
    monkeypatch.undo()
