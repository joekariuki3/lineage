from flask import url_for


def login_test_user_1(client, test_user_1):
    """
    Logs a test user into the application using the provided client and credentials.

    Parameters:
    client : Any
        The test client used to simulate HTTP requests to the application.
    test_user_1 : Any
        An object representing the first test user with an email attribute.

    Returns:
    Any
        The HTTP response object resulting from the login POST request.
    """
    return client.post(url_for("auth.login"), data={"email": test_user_1.email, "password": "user1password"})
