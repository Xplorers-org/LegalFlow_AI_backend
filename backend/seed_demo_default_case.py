import asyncio
import os
import sys
from datetime import date

# Insert parent directory to path to support running directly or as a module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.tenant import Tenant
from backend.app.models.lease import Lease, LeaseStatus
from backend.app.models.payment import Payment, PaymentStatus
from backend.app.models.case import Case, CaseStatus
from sqlalchemy import select

async def seed_demo_default_case():
    """Seeds a realistic commercial tenant default case to test demand letter generation."""
    async with AsyncSessionLocal() as db:
        # Check if tenant already exists
        email = "silvaretailers@gmail.com"
        existing_tenant = (await db.execute(select(Tenant).filter(Tenant.email == email))).scalars().first()

        if existing_tenant:
            print(f"[INFO] Demo Tenant '{email}' already exists. Skipping seed to prevent duplicate data.")
            return

        print("[SEED] Seeding Kamal Silva default case scenario...")

        # 1. Create Tenant
        tenant = Tenant(
            name="Mr. Kamal Silva",
            company="Silva Retailers",
            email=email,
            phone="+94778765432",
            nic_passport="198512345V",
            registration_no="PV-123456",
            address="Silva Retailers, Main Street, Colombo 03"
        )
        db.add(tenant)
        await db.flush()  # Populates tenant.id

        # 2. Create Lease
        extracted_metadata = {
            "first_schedule": {
                "physical_address": "Shop No. 12, Liberty Plaza, 250 R. A. De Mel Mawatha, Colombo 03",
                "assessment_number": "MC-45-A",
                "local_authority": "Colombo Municipal Council",
                "lot_plan_reference": "Lot 4 in Block B of Plan No. 450",
                "extent": "450 sq ft",
                "permitted_use": "Retail of clothing and fashion accessories"
            },
            "second_schedule_breakdown": {
                "base_rent": 180000.00,
                "building_security": 10000.00,
                "common_area_cleaning": 5000.00,
                "common_area_lighting": 3000.00,
                "elevator_lift_maintenance": 2000.00,
                "annual_escalation": "10% compounding annually on the anniversary of the lease start"
            },
            "third_schedule_utilities": {
                "electricity_provider": "Ceylon Electricity Board (CEB)",
                "electricity_account_no": "1023456789",
                "water_provider": "National Water Supply & Drainage Board (NWSDB)",
                "water_account_no": "9087654321",
                "liability_for_consumption": "Lessee, exclusively, from the Commencement Date",
                "recovery_of_arrears_on_termination": "Firstly from the Security Deposit; balance recoverable by civil action"
            }
        }

        lease = Lease(
            tenant_id=tenant.id,
            property_name="Shop No. 12, Liberty Plaza",
            property_address="250 R. A. De Mel Mawatha, Colombo 03",
            monthly_rent=180000.00,
            deposit=540000.00,
            service_charge=20000.00,
            payment_day=5,
            grace_period_days=5,
            interest_rate_pa=12.0,
            lease_start=date(2026, 1, 1),
            lease_end=date(2028, 12, 31),
            status=LeaseStatus.ACTIVE,
            extracted_metadata=extracted_metadata
        )
        db.add(lease)
        await db.flush()  # Populates lease.id

        # 3. Create Overdue Payments (June & July 2026)
        payment_june = Payment(
            lease_id=lease.id,
            amount_due=200000.00,
            amount_paid=0.00,
            due_date=date(2026, 6, 5),
            status=PaymentStatus.OVERDUE,
            gateway="PayHere"
        )
        payment_july = Payment(
            lease_id=lease.id,
            amount_due=200000.00,
            amount_paid=0.00,
            due_date=date(2026, 7, 5),
            status=PaymentStatus.OVERDUE,
            gateway="PayHere"
        )
        db.add(payment_june)
        db.add(payment_july)

        # 4. Create Case Record
        financial_facts = {
            "monthly_rent": 180000.00,
            "service_charge": 20000.00,
            "total_outstanding_arrears": 400000.00,
            "total_statutory_interest_accrued": 0.00,
            "grand_total_payable": 400000.00,
            "max_overdue_days": 26
        }

        case_record = Case(
            lease_id=lease.id,
            status=CaseStatus.OPEN,
            total_arrears=400000.00,
            overdue_days=26,
            risk_score="HIGH",
            recommended_action="LETTER_OF_DEMAND",
            ai_reasoning="Silva Retailers has defaulted on 2 consecutive monthly rent payments (June and July 2026). Total arrears have reached LKR 400,000.00. Recommend immediate issuance of a formal Letter of Demand under Section 4 of Rent Act No. 7 of 1972 and Section 3 of Recovery of Possession Act No. 1 of 2023.",
            financial_facts_json=financial_facts
        )
        db.add(case_record)

        await db.commit()
        print("[SUCCESS] Demo default case for Silva Retailers seeded successfully!")
        print(f"   Tenant Name: Mr. Kamal Silva")
        print(f"   Property: Shop No. 12, Liberty Plaza")
        print(f"   Total Arrears: LKR 400,000.00")
        print(f"   Recommended Action: LETTER_OF_DEMAND")

if __name__ == "__main__":
    asyncio.run(seed_demo_default_case())
