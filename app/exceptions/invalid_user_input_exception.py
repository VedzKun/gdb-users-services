from .user_management_exception_base import UserManagementException

class InvalidUserInputException(UserManagementException):
    """Raised when user input validation fails."""

    def __init__(self, field: str, reason: str):
        """Initialize InvalidUserInputException."""
        super().__init__(
            status_code=400,
            detail=f"Invalid {field}: {reason}",
            error_code="INVALID_USER_INPUT",
        )
