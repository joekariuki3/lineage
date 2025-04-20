from app.extensions import db
from app.models import User
from typing import Tuple

def saveUser(name: str, email: str, password: str) -> Tuple[int, Tuple[str, str]]:
    """
    Save a user to the database.

    Args:
        name (str): The user's name.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        Tuple[int, Tuple[str, str]]: A tuple containing the HTTP status code and a tuple of a message and a type.
            - The HTTP status code is either 201, 409, 500.
            - The message is a success or error message.
            - The type is either "success" or "error".
    """
    if checkUserExists(email):
        return 409, ("User already exists, try logging in", "error")
    try:
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return 201, (f"{user.name} information have been saved successfully", "success")
    except Exception:
        return 500, ("Something went wrong saving user information", "error")

def checkUserExists(email: str) -> bool:
    """
    Checks if a user with the given email address exists in the database.

    Args:
        email (str): The email address of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return db.session.query(db.exists().where(User.email == email)).scalar()
