
from app.extensions import db
from app.models import User
from app.services.service_base import service_response


class UserService:
    """
    Provides user management services such as user creation, retrieval, updates, and checks for
    user existence.

    The UserService class acts as an intermediary for managing user-related operations with a
    backend database. It provides methods to verify user existence, add new users, retrieve user
    details, and update user information. Uses dependency injection for database sessions to
    enhance testability and flexibility.
    """

    def __init__(self, db_session=None):
        """
        Initializes an instance of the class and sets up the database session.

        Attributes:
        db : The database session used for database operations. If no session is
            provided, defaults to the app's default database session.

        Args:
        db_session (Optional): The database session to be used. Defaults to
            None, in which case the app's default database session is used.
        """
        self.db = db_session or db.session

    def check_user_exists(self, email: str) -> bool:
        """
        Checks if a user with the specified email exists in the database.

        This function queries the database to determine whether a user account is
        associated with the provided email address.

        Args:
        email: The email address to check for existence in the database.

        Returns:
        bool: True if a user with the specified email exists, False otherwise.
        """
        return self.db.query(db.exists().where(User.email == email)).scalar()

    def create_user(self, name: str, email: str, password: str) -> tuple[dict, int]:
        """
        Creates a new user and adds it to the database.

        This method attempts to create a new user with the specified name, email,
        and password. If a user with the given email already exists, it returns a
        response indicating the conflict. If the user creation is successful, the
        new user is added to the database and a success response is returned.
        In case of any exceptions during the process, the database transaction is
        rolled back and an error response is provided.

        Parameters:
        name: str
            The name of the user to be created.
        email: str
            The email address of the user to be created.
        password: str
            The password for the user to be created.

        Returns:
        Tuple[dict, int]
            A tuple containing the service response dictionary and HTTP status code.
        """
        try:
            if self.check_user_exists(email):
                return service_response(409, "User already exists, try logging in", "warning", None)
            user = User(name=name, email=email, password=password)
            self.db.add(user)
            self.db.commit()
            return service_response(201, "User created successfully", "success", user)
        except Exception as e:
            self.db.rollback()
            print(f"Error creating user: {e!s}")
            return service_response(500, "Something went wrong creating user", "danger", None)

    def get_user(self, email: str | None = None, user_id: int | None = None) -> tuple[dict, int]:
        """
        Retrieves a user from the database based on email or user_id. The function allows searching by either
        the email or user ID to locate a single user record. You can provide one or the other,
        but not both simultaneously for the operation to succeed. It handles common scenarios like
        missing inputs, no user found, and unexpected exceptions during the lookup.

        Args:
            email: str
                The email address of the user to retrieve. Optional if user_id is provided.
            user_id: Union[int, None]
                The unique user ID corresponding to the user in the database. Optional if email is provided.

        Returns:
            Tuple[dict, int]
                A response tuple containing a dictionary with details about the operation
                and the corresponding HTTP status code.
        """
        try:
            if not email and not user_id:
                return service_response(400, "Email or user_id is required", "error", None)

            query = self.db.query(User)
            if email:
                query = query.filter_by(email=email)
            else:
                query = query.filter_by(user_id=user_id)

            user = query.first()

            if not user:
                return service_response(404, "User not found", "warning", None)

            return service_response(200, "User found", "success", user)
        except Exception as e:
            print(f"Error retrieving user: {e!s}")
            return service_response(500, "Something went wrong retrieving user", "danger", None)

    def update_user(self, user: User, **kwargs) -> tuple[dict, int]:
        """
        Updates the attributes of the provided user object based on the keyword arguments and commits the
        changes to the database. If a password update is included, it is properly hashed before being set.
        If the update process encounters an error, the database transaction is rolled back.

        Args:
            user (User): The user object whose information needs to be updated.
            **kwargs: Arbitrary keyword arguments representing the fields to be updated.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary representing the response and corresponding
            HTTP status code.
        """
        try:
            for key, value in kwargs.items():
                if key == "password":
                    user.set_password(value)
                elif key == "emailVerify":
                    user.emailVerify = value
                else:
                    setattr(user, key, value)
            self.db.commit()
            return service_response(200, "User updated successfully", "success", user)
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e!s}")
            return service_response(500, "Something went wrong updating user information", "error", None)