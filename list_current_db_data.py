import asyncio
import os
import sys

from backend.app.core.database import AsyncSessionLocal
from sqlalchemy import select
from backend.app.models.tenant import Tenant
from backend.app.models.lease import Lease
from backend.app.models.payment import Payment
from backend.app.models.case import Case

async def list_data():
    async with AsyncSessionLocal() as db:
        # Get Tenants
        tenants = (await db.execute(select(Tenant))).scalars().all()
        print(f"=== Tenants ({len(tenants)}) ===")
        for t in tenants:
            print(f"ID: {t.id} | Name: {t.name} | Company: {t.company} | Email: {t.email}")

        # Get Leases
        leases = (await db.execute(select(Lease))).scalars().all()
        print(f"\n=== Leases ({len(leases)}) ===")
        for l in leases:
            print(f"ID: {l.id} | Tenant ID: {l.tenant_id} | Property: {l.property_name} | Rent: {l.monthly_rent} | Status: {l.status}")

        # Get Payments
        payments = (await db.execute(select(Payment))).scalars().all()
        print(f"\n=== Payments ({len(payments)}) ===")
        for p in payments:
            print(f"ID: {p.id} | Lease ID: {p.lease_id} | Amount: {p.amount_due} | Due: {p.due_date} | Status: {p.status}")

        # Get Cases
        cases = (await db.execute(select(Case))).scalars().all()
        print(f"\n=== Cases ({len(cases)}) ===")
        for c in cases:
            print(f"ID: {c.id} | Lease ID: {c.lease_id} | Status: {c.status} | Arrears: {c.total_arrears} | Action: {c.recommended_action}")

if __name__ == "__main__":
    asyncio.run(list_data())
