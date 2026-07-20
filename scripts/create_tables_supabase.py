import asyncio
import os
import sys

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.models import BaseModel


async def init_supabase_tables():
    """Initializes and creates all LegalFlow AI ORM tables directly in Supabase."""
    print("Connecting to Supabase PostgreSQL Database...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")

    async with engine.begin() as conn:
        print("Creating tables: users, tenants, leases, payments, cases, documents, audit_logs...")
        await conn.run_sync(BaseModel.metadata.create_all)

    print("✅ All LegalFlow AI tables successfully created in Supabase!")


if __name__ == "__main__":
    asyncio.run(init_supabase_tables())
