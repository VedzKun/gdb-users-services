from .user_management_exception_base import UserManagementException

class UserInactiveException(UserManagementException):
    """Raised when attempting to edit an inactive user."""

    def __init__(self, login_id: str):
        """Initialize UserInactiveException."""
        super().__init__(
            status_code=403,
            detail=f"User with login_id '{login_id}' is inactive",
            error_code="USER_INACTIVE",
        )
