"""
Seed Users Data Script

This script populates the users table with sample users for testing.
Creates users with MANAGER, TELLER, and ADMIN roles.

All passwords are hashed using bcrypt with the default password: "Welcome@1"

Usage:
    python seed_users.py
"""

import asyncio
import asyncpg
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def seed_users():
    """Seed the users table with sample data."""
    
    host = "localhost"
    port = 5432
    user = "postgres"
    password = "anil"
    db_name = "gdb_users_db"
    
    # Default password for all users
    default_password = "Welcome@1"
    hashed_password = hash_password(default_password)
    
    # Sample users to create
    users = [
        # ADMIN users
        {
            "username": "Admin User",
            "login_id": "admin",
            "password": hashed_password,
            "role": "ADMIN",
            "is_active": True
        },
        {
            "username": "Sarah Johnson",
            "login_id": "sarah.admin",
            "password": hashed_password,
            "role": "ADMIN",
            "is_active": True
        },
        
        # TELLER users
        {
            "username": "John Doe",
            "login_id": "john.doe",
            "password": hashed_password,
            "role": "TELLER",
            "is_active": True
        },
        {
            "username": "Emily Davis",
            "login_id": "emily.davis",
            "password": hashed_password,
            "role": "TELLER",
            "is_active": True
        },
        
        # MANAGER users (formerly CUSTOMER)
        {
            "username": "Jane Smith",
            "login_id": "jane.smith",
            "password": hashed_password,
            "role": "MANAGER",
            "is_active": True
        },
        {
            "username": "Michael Brown",
            "login_id": "michael.brown",
            "password": hashed_password,
            "role": "MANAGER",
            "is_active": True
        },
        {
            "username": "Alice Wilson",
            "login_id": "alice.wilson",
            "password": hashed_password,
            "role": "MANAGER",
            "is_active": True
        },
        {
            "username": "Bob Taylor",
            "login_id": "bob.taylor",
            "password": hashed_password,
            "role": "MANAGER",
            "is_active": True
        },
    ]
    
    try:
        print("=" * 60)
        print("🌱 Seeding Users Data")
        print("=" * 60)
        print()
        
        print(f"📡 Connecting to {db_name}...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        
        print(f"✅ Connected to {db_name}\n")
        
        # Check if users already exist
        existing_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing users")
            response = input("Do you want to delete existing users and reseed? (yes/no): ")
            if response.lower() == 'yes':
                print("🗑️  Deleting existing users...")
                await conn.execute("DELETE FROM users")
                print("✅ Existing users deleted\n")
            else:
                print("❌ Seeding cancelled")
                await conn.close()
                return
        
        # Insert users
        print(f"📝 Inserting {len(users)} users...")
        print()
        
        for user_data in users:
            await conn.execute("""
                INSERT INTO users (username, login_id, password, role, is_active)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                user_data["username"],
                user_data["login_id"],
                user_data["password"],
                user_data["role"],
                user_data["is_active"]
            )
            
            print(f"   ✓ {user_data['username']} ({user_data['login_id']}) - {user_data['role']}")
        
        print()
        
        # Verify insertion
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        role_counts = await conn.fetch("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role 
            ORDER BY role
        """)
        
        print("📊 Database Statistics:")
        print(f"   Total Users: {total_users}")
        for row in role_counts:
            print(f"   {row['role']}: {row['count']}")
        
        await conn.close()
        
        print()
        print("=" * 60)
        print("✅ Users seeded successfully!")
        print("=" * 60)
        print()
        print("📝 Login Credentials (all users):")
        print(f"   Password: {default_password}")
        print()
        print("   Sample logins:")
        print("   - ADMIN:   admin / Welcome@1")
        print("   - TELLER:  john.doe / Welcome@1")
        print("   - MANAGER: jane.smith / Welcome@1")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(seed_users())
