"""
Install dependency if needed:
    pip install asyncpg python-dotenv
"""

import asyncio
import os

import asyncpg
from dotenv import load_dotenv

# Load .env file
load_dotenv()


async def test_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing in .env")

    print("Connecting to:")
    print(database_url.split("@")[-1])  # hide username/password

    # Remove asyncpg driver prefix if present
    database_url = database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://"
    )

    try:
        conn = await asyncpg.connect(
            database_url,
            ssl="require"
        )

        print("✅ Connected to Supabase PostgreSQL")

        # Test query
        version = await conn.fetchval("SELECT version();")
        print("\nPostgreSQL version:")
        print(version)

        # Check tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            ORDER BY table_name;
        """)

        print("\nTables:")
        if tables:
            for table in tables:
                print("-", table["table_name"])
        else:
            print("No tables found")

        await conn.close()

    except Exception as e:
        print("❌ Connection failed")
        print(type(e).__name__, e)


if __name__ == "__main__":
    asyncio.run(test_connection())