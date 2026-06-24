#!/usr/bin/env python3
"""
Users Service Database Reset Script
Purpose: Drop and recreate the database (FOR DEVELOPMENT ONLY)
WARNING: This will delete all data in the database!
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
os.chdir(current_dir)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def reset_database():
    """Drop and recreate the database (FOR DEVELOPMENT ONLY)"""
    try:
        import asyncpg
        
        # Load database config from .env
        db_host = os.getenv('DATABASE_HOST', 'localhost')
        db_port = int(os.getenv('DATABASE_PORT', 5432))
        db_name = os.getenv('DATABASE_NAME', 'gdb_users_db')
        db_user = os.getenv('DATABASE_USER', 'postgres')
        db_password = os.getenv('DATABASE_PASSWORD', '')
        
        logger.warning("=" * 70)
        logger.warning("⚠️  DATABASE RESET - ALL DATA WILL BE DELETED!")
        logger.warning("=" * 70)
        logger.warning(f"\nTarget database: {db_name}")
        logger.warning(f"Host: {db_host}:{db_port}")
        
        # Connect to default 'postgres' database to drop and recreate
        logger.info("\n1. Connecting to PostgreSQL server...")
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres',
        )
        
        try:
            # Terminate existing connections to the database
            logger.info(f"\n2. Terminating existing connections to {db_name}...")
            await conn.execute(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                  AND pid <> pg_backend_pid();
                """
            )
            
            # Drop the database
            logger.info(f"\n3. Dropping database: {db_name}...")
            await conn.execute(f"DROP DATABASE IF EXISTS {db_name};")
            logger.info(f"✓ Database dropped successfully")
            
            # Create the database
            logger.info(f"\n4. Creating database: {db_name}...")
            await conn.execute(f"CREATE DATABASE {db_name};")
            logger.info(f"✓ Database created successfully")
            
        finally:
            await conn.close()
        
        # Now run the schema setup
        logger.info("\n5. Setting up database schema...")
        from setup_db import setup_database
        success = await setup_database()
        
        if success:
            logger.info("\n" + "=" * 70)
            logger.info("✅ DATABASE RESET AND SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
        
        return success
        
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("DATABASE RESET FAILED!")
        logger.error("=" * 70)
        logger.error(f"Error: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure PostgreSQL is running")
        logger.error("2. Verify credentials in .env file")
        logger.error("3. Check that you can connect to the 'postgres' database")
        logger.error("=" * 70)
        return False


async def main():
    """Main entry point"""
    try:
        success = await reset_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
