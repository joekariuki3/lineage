from http import HTTPStatus


def service_response(status_code: int, message: str, category: str, data: dict | list | None) -> tuple[dict, int]:
    """
    Generates a standard response for a service in the application.

    Args:
        status_code (int): The HTTP status code to return (100-599) (HTTPStatus.CONTINUE-HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED).
        message (str): A message to the user.
        category (str): Response category. Must be one of: 'success', 'error', 'warning', 'danger'.
        data (Union[dict, List, None]): Additional data to include in the response.

    Returns:
        Tuple[dict, int]: A tuple containing:
            - dict: Response with keys: 'data', 'message', 'category'
            - int: HTTP status code

    Raises:
        ValueError: If status_code or category are invalid
    """
    valid_categories = {'success', 'error', 'warning', 'danger'}
    if not isinstance(status_code, int) or not HTTPStatus.CONTINUE <= status_code <= HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED:
        raise ValueError("Invalid HTTP status code")
    if category not in valid_categories:
        raise ValueError(f"Category must be one of: {', '.join(sorted(valid_categories))}")

    return {
        "data": data,
        "message": str(message),
        "category": category
    }, status_code