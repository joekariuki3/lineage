from app.extensions import db
from app.models import User
from typing import Tuple, Union, Optional

def create_user(name: str, email: str, password: str) -> User:
    """
    Creates a new user in the database.

    Args:
        name (str): The name of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
    Returns:
        User: The created user object.
    Raises:
        Exception: If there is an error creating the user.
    """
    try:
        user = User(name=name, email=email)
        user.set_password(password)
        return user
    except Exception as e:
        raise Exception(f"Error creating user: {str(e)}")

def save_user(user: User) -> Tuple[int, str, str]:

    if check_user_exists(user.email):
        return 409, "User already exists, try logging in", "error"
    try:
        db.session.add(user)
        db.session.commit()
        return 201, f"{user.name} information has been saved successfully", "success"
    except Exception as e:
        db.session.rollback()
        print(f"Error saving user: {str(e)}")
        return 500, "Something went wrong saving user information", "error"

def check_user_exists(email: str) -> bool:
    """
    Checks if a user with the given email address exists in the database.

    Args:
        email (str): The email address of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return db.session.query(db.exists().where(User.email == email)).scalar()

def get_user(email=None, id=None) -> Union[User, None]:
    """
    Retrieves a user from the database by email or id.

    Args:
        email (str): The email address of the user.
        id (int): The id of the user.

    Returns:
        User: The user object.
    """
    if email:
        return db.session.query(User).filter_by(email=email).first()
    elif id:
        return db.session.query(User).filter_by(user_id=id).first()
    else:
        return None

def update_user(user: User, **kwargs) -> Tuple[int, str, str]:
    """
    Updates a user in the database.
    Args:
        user (User): The user object to update.
        **kwargs: Additional keyword arguments to update the user.

    Returns:
        Tuple[int, Tuple[str, str]]: A tuple containing the HTTP status code and a message tuple.
    """
    try:
        for key, value in kwargs.items():
            if key == "password":
                user.set_password(value)
            elif key == "emailVerify":
                user.emailVerify = value
            else:
                setattr(user, key, value)
        db.session.commit()
        return 200, f"{user.name} information has been updated successfully", "success"
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}")
        return 500, "Something went wrong updating user information", "error"