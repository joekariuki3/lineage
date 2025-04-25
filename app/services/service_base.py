from typing import Tuple, Union, List
def service_response(status_code: int, message: str, category: str, data: Union[dict, List, None]) -> Tuple[dict, int]:
    """
    Generates a standard response for a service in the application.

    Args:
        status_code (int): The HTTP status code to return.
        message (str): A message to the user.
        category (str): A category to group the response under. Should be 'success', 'error', or 'warning'.
        data (Union[dict, List, None]): Additional data to include in the response.

    Returns:
        Tuple[dict, int]: A tuple containing a dictionary with the message, category, and data, and the status code.
    """

    return {
        "data": data,
        "message": message,
        "category": category
    }, status_code