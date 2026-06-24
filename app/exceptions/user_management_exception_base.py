from fastapi import HTTPException
from typing import Optional

class UserManagementException(HTTPException):
    """
    Base exception for all user management operations.

    Attributes:
        status_code: HTTP status code
        detail: Error message
        error_code: Custom error code for client handling
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = "USER_MANAGEMENT_ERROR",
    ):
        """Initialize UserManagementException."""
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
