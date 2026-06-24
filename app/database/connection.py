"""
User Management Service - Database Connection Management

This module provides async database connection pooling using asyncpg.
Raw SQL operations only - no ORM.
"""

import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages asyncpg connection pool for PostgreSQL.
    
    Provides async context managers for database operations.
    Ensures proper resource cleanup and connection pooling.
    """
    
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection URL
            min_size: Minimum pool size
            max_size: Maximum pool size
        """
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """
        Create connection pool.
        
        Raises:
            asyncpg.PostgresError: If connection fails
        """
        try:
            self.pool = await asyncpg.create_pool(dsn=self.database_url, init=set_schema_search_path,
                min_size=self.min_size,
                max_size=self.max_size,
                timeout=10,
                command_timeout=10
            )
            logger.info("✅ Database connection pool established")
        except Exception as e:
            # TODO: [M06-Bug-01] BUG: The service starts up silently even if the database is dead, causing downstream failures. Consider how this exception should be propagated.
            # Bug (M06-Bug-01): Generic exception block swallows connection errors.
            # Swallowing the connection error prevents immediate startup crashes,
            # but leads to delayed, confusing AttributeError crashes when querying.
            logger.error(f"⚠️ Exception occurred during database connection pool setup")
            raise e
    
    async def disconnect(self) -> None:
        """
        Close all connections in pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def transaction(self):
        """
        Async context manager for transaction management.
        
        Yields:
            asyncpg.Connection: Database connection with active transaction
            
        Usage:
            async with db_manager.transaction() as conn:
                await conn.execute("INSERT INTO ...")
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a single connection from pool.
        
        Yields:
            asyncpg.Connection: Database connection
            
        Usage:
            async with db_manager.get_connection() as conn:
                result = await conn.fetch("SELECT ...")
        """
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args):
        """
        Execute a query that doesn't return results.
        
        Args:
            query: SQL query string
            *args: Query parameters
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """
        Fetch multiple rows from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of records as dictionaries
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """
        Fetch a single row from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single record as dictionary or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """
        Fetch a single value from database.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value or None
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


async def init_db():
    """
    Initialize database connection pool.
    Called during application startup.
    Also handles automatic database creation, schema execution, and seeding.
    """
    global db_manager
    from pathlib import Path
    
    # Build database URL from environment variables
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'gdb_users_db')
    db_user = os.getenv('DATABASE_USER', 'postgres')
    db_password = os.getenv('DATABASE_PASSWORD', '')
    
    # 1. Connect to postgres default DB to verify/create target DB
    try:
        logger.info(f"Checking if database {db_name} exists...")
        temp_conn = await asyncpg.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            database="postgres"
        )
        db_exists = await temp_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        if not db_exists:
            logger.info(f"📦 Creating database: {db_name}")
            await temp_conn.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ Database created: {db_name}")
        else:
            logger.info(f"✅ Database already exists: {db_name}")
        await temp_conn.close()
    except Exception as e:
        logger.error(f"⚠️ Error verifying/creating database {db_name}: {e}")

    if db_password:
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        database_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    logger.info(f"🚀 Initializing database connection to {db_name}@{db_host}:{db_port}")
    
    db_manager = DatabaseManager(database_url)
    await db_manager.connect()
    logger.info("✅ Database pool established")

    # 2. Check if tables exist, run schema and seed if necessary
    try:
        async with db_manager.get_connection() as conn:
            users_table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = 'users')"
            )
            
            if not users_table_exists:
                logger.info("📋 Core table 'users' does not exist. Running users_schema.sql...")
                schema_path = Path(__file__).parent / "users_schema.sql"
                if schema_path.exists():
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema_sql = f.read()
                    await conn.execute(schema_sql)
                    logger.info("✅ Schema executed successfully")
                else:
                    logger.error(f"❌ Schema file not found at {schema_path}")
            
            # Check user counts and seed default users
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            if user_count == 0:
                logger.info("🌱 Seeding default users...")
                import bcrypt
                
                # Hash default password
                default_password = "Welcome@1"
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), salt).decode('utf-8')
                
                users_to_seed = [
                    ("Admin User", "admin", hashed_password, "ADMIN", True),
                    ("Sarah Johnson", "sarah.admin", hashed_password, "ADMIN", True),
                    ("John Doe", "john.doe", hashed_password, "TELLER", True),
                    ("Emily Davis", "emily.davis", hashed_password, "TELLER", True),
                    ("Teller User", "teller", hashed_password, "TELLER", True),
                    ("Manager User", "manager.manager", hashed_password, "MANAGER", True),
                    ("Jane Smith", "jane.smith", hashed_password, "MANAGER", True),
                    ("Michael Brown", "michael.brown", hashed_password, "MANAGER", True),
                    ("Alice Wilson", "alice.wilson", hashed_password, "MANAGER", True),
                    ("Bob Taylor", "bob.taylor", hashed_password, "MANAGER", True)
                ]
                
                for username, login_id, pwd, role, is_active in users_to_seed:
                    await conn.execute(
                        """
                        INSERT INTO users (username, login_id, password, role, is_active)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        username, login_id, pwd, role, is_active
                    )
                logger.info(f"✅ Seeded {len(users_to_seed)} default users successfully")
    except Exception as e:
        logger.error(f"❌ Error during schema verification/seeding: {e}")
        raise


async def close_db():
    """
    Close database connection pool.
    Called during application shutdown.
    """
    global db_manager
    
    if db_manager:
        await db_manager.disconnect()
        db_manager = None
        logger.info("✅ Database closed successfully")


def get_db() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: The active database manager
        
    Raises:
        RuntimeError: If database manager is not initialized
    """
    if db_manager is None:
        raise RuntimeError("Database manager is not initialized. Call init_db() first.")
    return db_manager

# Schema configuration for multi-tenant database
SCHEMA_NAME = "users_service"

# Update search_path for PostgreSQL
async def set_schema_search_path(connection):
    """Set the search path to use the correct schema."""
    await connection.execute(f"SET search_path TO users_service, public")
