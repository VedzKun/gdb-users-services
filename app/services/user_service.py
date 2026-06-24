import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# CR (M06-CR-01): Built-in Exception Handling
# TODO: Implement proper try-except blocks for built-in exceptions:
# - Catch KeyError if required fields (like 'login_id' or 'user_id') are missing.
# - Catch ValueError if 'user_id' cannot be converted to an integer.
# - Log the details of the caught error and return a safe default dictionary or raise a clean warning.

class UserServiceHelper:
    """
    Helper for user record transformation.
    """
    
    @staticmethod
    def format_raw_user(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw user database dict into application format.
        """
        try:
            user_id = int(raw_data["user_id"])
            login_id = raw_data["login_id"]
            role = raw_data.get("role", "TELLER")
            
            return {
                "id": user_id,
                "login": login_id,
                "role": role.upper()
            }
        except KeyError as e:
            logger.error(f"Malformed user record: missing required field {e}")
            raise ValueError(f"Malformed user record: missing required field {e}")
        except ValueError as e:
            logger.error(f"Malformed user record: invalid user_id format {e}")
            raise ValueError(f"Malformed user record: invalid user_id format {e}")
