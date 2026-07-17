from app.models.user import User


def test_user_initialization():
    """
    Test the initialization of a User instance.
    Verifies that attributes are correctly set.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="secure-password")
    assert user.name == "John Doe"
    assert user.email == "john.doe@example.com"
    assert user.password != "secure-password"  # Password should be hashed


def test_set_password():
    """
    Test the set_password method to ensure it hashes passwords properly.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="initial-password")
    user.set_password("new-secure-password")
    assert user.password != "new-secure-password"
    assert user.check_password("new-secure-password") is True


def test_check_password():
    """
    Test the check_password method to verify password validation.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="mypassword")
    assert user.check_password("mypassword") is True
    assert user.check_password("wrong-password") is False


def test_get_id():
    """
    Test the get_id method to ensure it returns the user's ID as a string.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="password")
    user.user_id = 123
    assert user.get_id() == "123"


def test_get_reset_password_token():
    """
    Test the get_reset_password_token method to validate token creation.
    """
    user = User(name="John Doe", email="john.doe@example.com", password="password")
    secret = "my-secret-key"
    token = user.get_reset_password_token(secret, 600)
    assert token is not None
    assert isinstance(token, str)


def test_verify_reset_password_token(session):
    """
    Test the verify_reset_password_token method to validate token decoding.
    """
    user = User(name="joel Doe", email="joel.doe@example.com", password="password")
    session.add(user)
    session.commit()

    secret = "my-secret-key"
    token = user.get_reset_password_token(secret, 600)
    verified_user = User.verify_reset_password_token(secret, token)
    assert verified_user