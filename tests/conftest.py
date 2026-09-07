from datetime import datetime

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Event, Family, Link, Member, User
from app.utils.constants import Gender
from config import TestConfig


@pytest.fixture(scope="function")
def app():
    """
    Fixture that provides an application instance for testing.

    This fixture creates an application instance configured with
    the `TestConfig` settings for testing purposes. It also ensures
    the application context is appropriately managed during the
    test session.

    Yields:
        flask.Flask: The application instance configured for testing.
    """
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db(app):
    """
    This fixture sets up a database for use in tests. It initializes the database, creates all
    tables, provides a database connection for the session, and ensures proper cleanup by
    removing the session and dropping all tables.

    Args:
        app (Fixture): A fixture that initializes the application for the test session.

    Yields:
        _db (database instance): The initialized database instance for use during the session.
    """
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture
def client(app):
    """
    Fixture that creates a test client for making requests in tests.

    Args:
        app: The Flask application fixture

    Returns:
        FlaskClient: A test client for making requests
    """
    return app.test_client()


@pytest.fixture(scope="function")
def session(db):
    """
    Fixture for providing a database session with transactional rollback.

    This pytest fixture provides a scoped database session that ensures
    all operations performed during a test are rolled back upon test completion.
    It creates a new connection and transaction for each test, binds the session
    to the transactional connection, and ensures cleanup is performed so that
    no database state persists across tests.

    Parameters:
        db (SQLAlchemy): The database instance to use for creating the session.

    Yields:
        SQLAlchemy Session: A session bound to the transaction, ensuring
        that any changes made during the test do not persist.

    """
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.bind = connection
    yield db.session
    transaction.rollback()
    connection.close()
    db.session.remove()


def clean_up(session, obj: Family | User | Member | Link | Event, obj_id: int):
    """
    Deletes a given object from the session and commits the changes if the object
    exists in the session. The function checks the existence of the object by its
    class and ID before performing the deletion and commit.

    Args:
        session: Database session used for object querying and manipulation.
        obj (Union[Family, User, Member, Link, Event]): The object intended for
            deletion from the session.
        obj_id (int): The unique identifier of the object to validate its
            existence in the session.
    """
    class_name = type(obj)
    if session.get(class_name, obj_id):
        session.delete(obj)
        session.commit()


@pytest.fixture
def test_family_1(session):
    """
    Fixture to create and manage a test Family object within a database session.

    This fixture is used to create a Family object with the name "Test Family 1",
    add it to the session, and commit the transaction. After yielding the
    Family object for testing purposes, the fixture ensures cleanup by
    removing the object from the database.

    Yields:
        Family: The Family object created and added to the session.
    """
    family = Family(name="Test Family 1")
    session.add(family)
    session.commit()
    yield family
    clean_up(session, family, family.family_id)


@pytest.fixture
def test_family_2(session):
    """
    Fixture to provide a reusable Family object for testing purposes.

    This fixture creates a Family object with a predefined name and interacts with
    the provided session to persist it into the database before yielding. After
    yielding the Family object to the test, it ensures cleanup by removing the
    Family object from the database.

    Yields:
        Family: A Family object initialized with the name "Test Family 2".
    """
    family = Family(name="Test Family 2")
    session.add(family)
    session.commit()
    yield family
    clean_up(session, family, family.family_id)


@pytest.fixture
def test_guest_user_1(session, app):
    """
    Creates a test fixture that provides a guest user for use in test cases.
    This fixture sets up a guest user with predefined attributes, adds
    them to the session, and cleans up by removing the user after the test.

    Parameters:
        session: Session
            The database session used for creating, committing, and
            deleting the guest user.
        app: Flask
            The Flask application instance from which the guest user's
            properties (such as name, email, and password) are retrieved.

    Yields:
        User
            The created guest user instance.
    """
    guest_user = User(
        name=app.config["GUEST_NAME"],
        email=app.config["GUEST_EMAIL"],
        password=app.config["GUEST_PASSWORD"],
    )
    session.add(guest_user)
    session.commit()
    yield guest_user
    clean_up(session, guest_user, guest_user.user_id)


@pytest.fixture
def test_user_1(session):
    """
    Fixture for creating and managing temporary User object for testing purposes.

    This fixture sets up a test user, adds it to the session, commits the session, and yields
    the user object for use in test functions. After the test, it cleans up by deleting the
    user from the session and committing the session to persist its removal.

    Yields:
        User: A temporary User object created for testing.

    Parameters:
        session (Session): A database session used to interact with the database.
    """
    user = User(name="Test User 1", email="user1@mail.com", password="user1password")
    session.add(user)
    session.commit()
    yield user
    clean_up(session, user, user.user_id)


@pytest.fixture
def test_user_2(session):
    """
    This function is a pytest fixture used to create and manage a test user in the test database session. It sets up a
    user, commits it to the session, and ensures proper cleanup after test execution.

    Yields:
        User: A User object instance created and added to the session.

    Args:
        session: The database session fixture.
    """
    user = User(name="Test User 2", email="user2@mail.com", password="user2password")
    session.add(user)
    session.commit()
    yield user
    clean_up(session, user, user.user_id)


@pytest.fixture
def test_event_1(session, test_family_1):
    """
    Provides a test fixture for an event object meant for testing purposes.

    This fixture creates an Event object with predefined attributes, adds it
    to the session, and commits the changes to the database. After the test
    is completed, the fixture ensures cleanup by deleting the event object
    from the session and committing the session.

    Parameters:
        session: Session
            SQLAlchemy session object used to handle database interactions
            during the test.
        test_family_1: Family
            Predefined family object containing the necessary attributes
            required for creating the event.

    Yields:
        Event
            The event object created within this test fixture.

    This ensures that the database remains in a consistent and clean state
    during and after test execution.
    """
    event = Event(
        event_date=datetime(25, 4, 1),
        event_name="event_1",
        family_id=test_family_1.family_id,
    )
    session.add(event)
    session.commit()
    yield event
    clean_up(session, event, event.event_id)


@pytest.fixture
def test_event_2(session, test_family_2):
    """
    Provides a test fixture for an event object meant for testing purposes.

    This fixture creates an Event object with predefined attributes, adds it
    to the session, and commits the changes to the database. After the test
    is completed, the fixture ensures cleanup by deleting the event object
    from the session and committing the session.

    Parameters:
        session: Session
            SQLAlchemy session object used to handle database interactions
            during the test.
        test_family_2: Family
            Predefined family object containing the necessary attributes
            required for creating the event.

    Yields:
        Event
            The event object created within this test fixture.

    This ensures that the database remains in a consistent and clean state
    during and after test execution.
    """
    event = Event(
        event_date=datetime(24, 4, 1),
        event_name="event_2",
        family_id=test_family_2.family_id,
    )
    session.add(event)
    session.commit()
    yield event
    clean_up(session, event, event.event_id)


@pytest.fixture
def test_link_1(session, test_family_1):
    """
    A pytest fixture for creating and managing a test Link object in the test database.

    Yields
    ------
    Link
        The Link object created and added to the database session for testing purposes.
    """
    link = Link(link="https://joelmuhoho.com", family_id=test_family_1.family_id)
    session.add(link)
    session.commit()
    yield link
    clean_up(session, link, link.link_id)


@pytest.fixture
def test_member_1(session, test_family_1):
    """
    Fixture to create and clean up a test member in the database for testing purposes.

    This fixture initializes a `Member` object with predefined attributes and associates it
    with a test family provided by `test_family_1`. The object is added to the session and
    saved in the database. It is provided to the caller for testing and is subsequently
    deleted to ensure cleanup and prevent test contamination.

    Attributes:
        session (Session): The database session for operations.
        test_family_1 (Family): A pre-existing test family associated with the member.

    Yields:
        Member: The created `Member` instance for temporary use in tests.
    """
    member = Member(
        first_name="member",
        last_name="one",
        family_id=test_family_1.family_id,
        gender=Gender.MALE.value,
    )
    session.add(member)
    session.commit()
    yield member
    clean_up(session, member, member.member_id)


@pytest.fixture
def test_member_2(session, test_family_1):
    """
    Creates and manages a pytest fixture for testing a Member entity associated with a
    Family entity in the database. This fixture initializes the test data, commits it
    to the session, yields the created Member instance for use in tests, and cleans
    up the data after the test execution.

    Args:
        session: A SQLAlchemy session fixture used for database operations.
        test_family_1: A pytest fixture providing a Family entity instance for association.

    Yields:
        Member: An instance of the Member entity created for testing purposes.
    """
    member = Member(
        first_name="member",
        last_name="two",
        family_id=test_family_1.family_id,
        gender=Gender.FEMALE.value,
    )
    session.add(member)
    session.commit()
    yield member
    clean_up(session, member, member.member_id)


@pytest.fixture
def test_member_3(session, test_family_1):
    """
    Fixture for setting up and tearing down a test `Member` object in the database.

    This fixture creates a `Member` object associated with a given `Family`, adds
    it to the database session, and commits the session. After the test is completed,
    the `Member` object is deleted from the database session. The fixture provides a
    way to prepare and manage testing of database-related functionality involving
    `Member` objects.

    Parameters:
        session: Database session used to handle database operations during the test.
        test_family_1: A pre-existing `Family` object used to associate the new
                       `Member` object.

    Yields:
        Member: The `Member` object created for the test case.
    """
    member = Member(
        first_name="member",
        last_name="three",
        family_id=test_family_1.family_id,
        gender=Gender.OTHER.value,
    )
    session.add(member)
    session.commit()
    yield member
    clean_up(session, member, member.member_id)


@pytest.fixture
def test_user_and_family(test_user_1, test_family_1, session):
    """
    Provides a pytest fixture that associates a test user with a test family and prepares it
    for testing. This fixture establishes a relationship between the user and the family,
    ensures the relationship is saved in the session, and yields the test data.

    Args:
        test_user_1: The test user object that will be associated with a family.
        test_family_1: The test family object to associate with the test user.
        session: The database session used to commit changes.

    Yields:
        tuple: A tuple containing the test user and test family objects after the
        association is established and persisted.
    """
    test_user_1.families.append(test_family_1)
    session.commit()
    yield test_user_1, test_family_1


@pytest.fixture
def test_user_with_one_family(test_user_1, test_family_1, session):
    """
    Fixture providing a test user associated with a single family. This fixture links
    the provided family instance to the test user by setting the appropriate user ID,
    commits the session changes, and yields the resulting user instance. It is intended
    to simplify testing scenarios where a user needs to be associated with exactly one
    family in the database.

    Args:
        test_user_1: A pytest fixture providing a test user instance.
        test_family_1: A pytest fixture providing a family instance.
        session: A pytest fixture providing the database session.

    Yields:
        The test user instance that is associated with the given family.
    """
    test_family_1.user_id = test_user_1.user_id
    session.commit()
    yield test_user_1


@pytest.fixture
def test_user_with_two_families(test_user_1, test_family_1, test_family_2, session):
    """
    Fixture for creating a test user associated with two families in the test database.

    The fixture assigns the same user ID to two test family objects and commits the changes
    to the provided database session. This simulates a scenario where a user is associated with
    two different families. The modified user object is yielded for use in tests.

    Args:
        test_user_1 (TestUser): A test user object to associate with test families.
        test_family_1 (TestFamily): A test family object to associate with the user.
        test_family_2 (TestFamily): Another test family object to associate with the user.
        session (Session): A database session used to commit the changes.

    Yields:
        TestUser: The test user object with associations to the two test families.
    """
    test_family_1.user_id = test_user_1.user_id
    test_family_2.user_id = test_user_1.user_id
    session.commit()
    yield test_user_1


@pytest.fixture
def test_family_with_a_link(test_family_1, test_link_1, session):
    """
    Creates and yields a test family object with an associated link. The link
    is appended to the test family, and the changes are committed to the session
    before yielding. This fixture is utilized for testing purposes to simulate
    a family object containing relevant links.

    Parameters:
    test_family_1: TestFamily
        A test family object used for associating with a link in the fixture.
    test_link_1: TestLink
        A test link object that is appended to the test family.
    session: Session
        A session object that handles database operations and commits changes.

    Yields:
    TestFamily
        The test family object with an associated link.

    """
    test_family_1.links.append(test_link_1)
    session.commit()
    yield test_family_1
