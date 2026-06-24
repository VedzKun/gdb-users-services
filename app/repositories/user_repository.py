"""
User Repository - Data access layer for users.
"""

import logging
import bcrypt
from typing import Optional, Dict, Any, List
from ..database.connection import get_db

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self):
        """Initialize repository."""
        self.db = get_db()
    
    async def create_user(self, username: str, login_id: str, password: str, role: str = "MANAGER") -> Dict[str, Any]:
        """Create a new user."""
        try:
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            query = """
                INSERT INTO users (username, login_id, password, role, is_active)
                VALUES ($1, $2, $3, $4, TRUE)
                RETURNING user_id, username, login_id, role, is_active, created_at, updated_at
            """
            
            user = await self.db.fetchrow(query, username, login_id, hashed_password, role)
            logger.info(f"✅ User created: {login_id}")
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Error creating user: {str(e)}")
            raise
    
    async def get_user_by_login_id(self, login_id: str) -> Optional[Dict[str, Any]]:
        """Get user by login ID."""
        try:
            query = """
                SELECT user_id, username, login_id, password, role, is_active, created_at, updated_at
                FROM users
                WHERE login_id = $1
            """
            user = await self.db.fetchrow(query, login_id)
            if user:
                user_dict = dict(user)
                logger.info(f"DEBUG: User {login_id} data from DB: {user_dict}, is_active type: {type(user_dict.get('is_active'))}")
                return user_dict
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            query = """
                SELECT user_id, username, login_id, password, role, is_active, created_at, updated_at
                FROM users
                WHERE user_id = $1
            """
            user = await self.db.fetchrow(query, user_id)
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Error fetching user: {str(e)}")
            raise
    
    async def update_user(self, user_id: int, username: Optional[str] = None, 
                         password: Optional[str] = None, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update user details."""
        try:
            updates = []
            params = []
            param_count = 1
            
            if username:
                updates.append(f"username = ${param_count}")
                params.append(username)
                param_count += 1
            
            if password:
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                updates.append(f"password = ${param_count}")
                params.append(hashed_password)
                param_count += 1
            
            if role:
                updates.append(f"role = ${param_count}")
                params.append(role)
                param_count += 1
            
            if not updates:
                return await self.get_user_by_id(user_id)
            
            updates.append("updated_at = NOW()")
            params.append(user_id)
            
            query = f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE user_id = ${len(params)}
                RETURNING user_id, username, login_id, password, role, is_active, created_at, updated_at
            """
            
            user = await self.db.fetchrow(query, *params)
            logger.info(f"✅ User updated: {user_id}")
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Error updating user: {str(e)}")
            raise
    
    async def inactivate_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Inactivate a user."""
        try:
            query = """
                UPDATE users
                SET is_active = FALSE, updated_at = NOW()
                WHERE user_id = $1
                RETURNING user_id, username, login_id, role, is_active, created_at, updated_at
            """
            user = await self.db.fetchrow(query, user_id)
            logger.info(f"✅ User inactivated: {user_id}")
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Error inactivating user: {str(e)}")
            raise
    
    async def activate_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Activate a user."""
        try:
            query = """
                UPDATE users
                SET is_active = TRUE, updated_at = NOW()
                WHERE user_id = $1
                RETURNING user_id, username, login_id, role, is_active, created_at, updated_at
            """
            user = await self.db.fetchrow(query, user_id)
            logger.info(f"✅ User activated: {user_id}")
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ Error activating user: {str(e)}")
            raise
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        try:
            query = """
                SELECT user_id, username, login_id, role, is_active, created_at, updated_at
                FROM users
                ORDER BY created_at DESC
            """
            users = await self.db.fetch(query)
            return [dict(user) for user in users]
        except Exception as e:
            logger.error(f"❌ Error fetching users: {str(e)}")
            raise
