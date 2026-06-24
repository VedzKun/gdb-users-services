from typing import Optional
from .user_management_exception_base import UserManagementException

class InvalidRoleException(UserManagementException):
    """Raised when an invalid role is provided."""

    def __init__(self, role: str, valid_roles: Optional[list] = None):
        """Initialize InvalidRoleException."""
        valid_roles_str = ", ".join(valid_roles) if valid_roles else "MANAGER, TELLER, ADMIN"
        super().__init__(
            status_code=400,
            detail=f"Invalid role '{role}'. Valid roles are: {valid_roles_str}",
            error_code="INVALID_ROLE",
        )
