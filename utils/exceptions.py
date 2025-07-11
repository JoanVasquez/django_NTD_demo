# ⚠️ base_app_exception.py - Base exception for predictable business errors


class BaseAppException(Exception):
    """
    ⚠️ Base exception for predictable, business-rule errors with
    customizable HTTP status codes for consistent API error responses.
    """

    def __init__(self, message, status_code=400, payload=None):
        """
        Initialize the BaseAppException.

        :param message: Human-readable error message.
        :param status_code: HTTP status code to return (default: 400).
        :param payload: Optional dictionary with additional data for the client.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        """
        Convert the exception into a dictionary for JSON responses.
        Includes the message, status, and any additional payload.
        """
        error_response = dict(self.payload)
        error_response["status"] = "error"
        error_response["message"] = self.message
        return error_response
