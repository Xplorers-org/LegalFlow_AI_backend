import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.repositories.user_repository import UserRepository
from backend.app.models.user import UserRole


async def seed_landlord():
    """Seeds an initial admin/landlord account into Supabase."""
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        email = "landlord@legalflow.lk"
        existing = await repo.get_by_email(email)

        if not existing:
            pwd_hash = get_password_hash("LegalFlow2026!")
            user_data = {
                "name": "Sri Lankan Landlord Admin",
                "email": email,
                "password_hash": pwd_hash,
                "role": UserRole.LANDLORD,
                "phone": "+94771234567",
            }
            user = await repo.create(user_data)
            await db.commit()
            print("✅ Initial Landlord Account Created!")
            print(f"   Email: {email}")
            print("   Password: LegalFlow2026!")
        else:
            print(f"ℹ️ Landlord Account ({email}) already exists in Supabase.")


if __name__ == "__main__":
    asyncio.run(seed_landlord())
