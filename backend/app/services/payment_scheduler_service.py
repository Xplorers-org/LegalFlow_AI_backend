from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.repositories.payment_repository import PaymentRepository
from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.lease_repository import LeaseRepository
from backend.app.services.financial_engine import FinancialEngine
from backend.app.models.payment import PaymentStatus
from backend.app.models.case import CaseStatus
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class PaymentSchedulerService:
    """Service responsible for payment schedule generation, overdue detection, and case escalation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.case_repo = CaseRepository(db)
        self.lease_repo = LeaseRepository(db)

    async def check_and_update_overdue_payments(self) -> dict:
        """Scans pending payments, updates overdue status, and creates/updates legal compliance cases."""
        today = date.today()
        logger.info("Running daily overdue payment detection job", date=today.isoformat())

        overdue_payments = await self.payment_repo.get_overdue_payments_before(today)
        updated_count = 0
        cases_created = 0

        for payment in overdue_payments:
            lease = await self.lease_repo.get(payment.lease_id)
            if not lease:
                continue

            overdue_days = FinancialEngine.calculate_overdue_days(payment.due_date, lease.grace_period_days, today)
            if overdue_days > 0 and payment.status != PaymentStatus.OVERDUE:
                payment.status = PaymentStatus.OVERDUE
                await self.payment_repo.update(payment.id, {"status": PaymentStatus.OVERDUE})
                updated_count += 1

            # Compile financial facts for the lease
            all_payments = await self.payment_repo.get_by_lease(lease.id)
            facts = FinancialEngine.compile_financial_facts(lease, all_payments, today)

            if facts["total_outstanding_arrears"] > 0:
                open_case = await self.case_repo.get_open_case_by_lease(lease.id)
                if not open_case:
                    case_data = {
                        "lease_id": lease.id,
                        "status": CaseStatus.OPEN,
                        "total_arrears": facts["grand_total_payable"],
                        "overdue_days": facts["max_overdue_days"],
                        "financial_facts_json": facts,
                    }
                    await self.case_repo.create(case_data)
                    cases_created += 1
                else:
                    await self.case_repo.update(open_case.id, {
                        "total_arrears": facts["grand_total_payable"],
                        "overdue_days": facts["max_overdue_days"],
                        "financial_facts_json": facts,
                    })

        logger.info(
            "Overdue payment check completed",
            updated_payments=updated_count,
            cases_created=cases_created
        )
        return {
            "status": "success",
            "overdue_payments_updated": updated_count,
            "cases_created_or_updated": cases_created,
        }
