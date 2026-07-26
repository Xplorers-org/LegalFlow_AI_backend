import asyncio
import os
import sys
from sqlalchemy import text

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.config import settings
from backend.app.core.database import engine

async def add_column():
    print("Connecting to Supabase PostgreSQL Database...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")

    async with engine.begin() as conn:
        print("Executing: ALTER TABLE leases ADD COLUMN IF NOT EXISTS extracted_metadata JSONB;")
        await conn.execute(text("ALTER TABLE leases ADD COLUMN IF NOT EXISTS extracted_metadata JSONB;"))
    
    print("✅ Successfully added extracted_metadata column to leases table in Supabase!")

if __name__ == "__main__":
    asyncio.run(add_column())
