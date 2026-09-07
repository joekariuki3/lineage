from flask import abort


def test_404_error(client):
    """
    Tests the 404 error handling of the application.

    This function verifies that when a non-existent endpoint is accessed,
    the application responds with a 404 status code and provides the
    appropriate "Page Not Found" message in the response data.

    Parameters:
    client : flask.testing.FlaskClient
        A test client instance for making requests to the Flask application.

    Returns:
    None
    """
    response = client.get("/not-found")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data

def test_internal_error_with_monkeypatch(client, session, monkeypatch):
    """
    Tests the functionality of the application in handling internal server errors (HTTP 500).
    Ensures that the session's rollback method is called when an unhandled exception occurs.

    Args:
        client: A test client object for simulating requests to the application.
        session: The database session object associated with the application.
        monkeypatch: A pytest utility used to modify or mock parts of the application
            during testing.

    Raises:
        None

    Returns:
        None
    """
    # Mock the rollback method
    rollback_called = []

    def mock_rollback():
        rollback_called.append(True)

    monkeypatch.setattr(session, "rollback", mock_rollback)

    @client.application.route('/cause_500')
    def cause_500():
        abort(500)

    response = client.get('/cause_500')

    assert rollback_called  # Check rollback mock was called
    assert response.status_code == 500
    assert b"An unexpected error has occurred" in response.data

    monkeypatch.undo()
