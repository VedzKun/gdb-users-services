#!/usr/bin/env python3
"""
Users Service Database Setup Script
Purpose: Create database tables and schema
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


async def setup_database():
    """Create database tables and schema"""
    try:
        import asyncpg
        
        # Load database config from .env
        db_host = os.getenv('DATABASE_HOST', 'localhost')
        db_port = int(os.getenv('DATABASE_PORT', 5432))
        db_name = os.getenv('DATABASE_NAME', 'gdb_users_db')
        db_user = os.getenv('DATABASE_USER', 'postgres')
        db_password = os.getenv('DATABASE_PASSWORD', '')
        
        logger.info("=" * 70)
        logger.info("🚀 SETTING UP DATABASE SCHEMA")
        logger.info("=" * 70)
        logger.info(f"\nTarget database: {db_name}")
        logger.info(f"Host: {db_host}:{db_port}")
        
        # Connect to the target database
        logger.info("\n1. Connecting to database...")
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        
        try:
            # Read and execute schema
            schema_file = Path(__file__).parent / "app" / "database" / "users_schema.sql"
            
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
                
            logger.info(f"\n2. Reading schema from {schema_file.name}...")
            with open(schema_file, "r") as f:
                schema_sql = f.read()

            logger.info("3. Creating database objects...")
            await conn.execute(schema_sql)
            logger.info("✓ Schema executed successfully")
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            return True
            
        finally:
            await conn.close()
        
    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error("❌ DATABASE SETUP FAILED!")
        logger.error("=" * 70)
        logger.error(f"Error: {str(e)}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure PostgreSQL is running")
        logger.error("2. Verify credentials in .env file")
        logger.error("3. Verify that the database exists")
        logger.error("=" * 70)
        return False


async def main():
    """Main entry point"""
    try:
        success = await setup_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
