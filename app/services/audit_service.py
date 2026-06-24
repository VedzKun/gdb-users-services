"""
Audit Service - Business logic for audit logging.
"""

import logging
import json
from typing import Optional, Dict, Any
from ..database.connection import get_db

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging."""
    
    @staticmethod
    async def log_action(
        user_id: int,
        action: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        performed_by: Optional[str] = None
    ) -> bool:
        """
        Log an audit action.
        
        Args:
            user_id: ID of the user affected
            action: Action type (CREATE, UPDATE, INACTIVATE, REACTIVATE, PASSWORD_CHANGE)
            old_data: Previous data (for updates)
            new_data: New data
            performed_by: Who performed the action
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db = get_db()
            
            # Convert dicts to JSON strings
            old_data_json = json.dumps(old_data) if old_data else None
            new_data_json = json.dumps(new_data) if new_data else None
            
            query = """
                INSERT INTO user_audit_logs (user_id, action, old_data, new_data, performed_by)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING log_id
            """
            
            result = await db.fetchval(
                query,
                user_id,
                action,
                old_data_json,
                new_data_json,
                performed_by
            )
            
            if result:
                logger.info(f"✅ Audit logged: {action} for user_id {user_id}")
                return True
            else:
                logger.error(f"❌ Failed to log audit: {action} for user_id {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error logging audit action: {str(e)}")
            # Don't raise - audit logging shouldn't break the main operation
            return False
