from datetime import date
from typing import List, Dict, Any
from backend.app.models.lease import Lease
from backend.app.models.payment import Payment, PaymentStatus


class FinancialEngine:
    """Deterministic financial calculation engine for commercial leases.
    
    IMPORTANT: All financial calculations (arrears, interest, overdue days, schedule validation)
    MUST be performed exclusively by this engine. The AI service ingests the resulting
    immutable facts and never performs arithmetic calculations.
    """

    @staticmethod
    def calculate_overdue_days(due_date: date, grace_period_days: int = 5, current_date: date = None) -> int:
        """Calculates days past due date including grace period."""
        if current_date is None:
            current_date = date.today()
        
        days_past_due = (current_date - due_date).days
        effective_overdue = days_past_due - grace_period_days
        return max(0, effective_overdue)

    @staticmethod
    def calculate_statutory_interest(
        principal_overdue: float,
        overdue_days: int,
        annual_rate_pct: float = 12.0
    ) -> float:
        """Calculates simple statutory interest per annum accrued on overdue commercial rent."""
        if principal_overdue <= 0 or overdue_days <= 0:
            return 0.0
        
        daily_rate = (annual_rate_pct / 100.0) / 365.0
        interest = principal_overdue * daily_rate * overdue_days
        return round(interest, 2)

    @classmethod
    def compile_financial_facts(
        cls,
        lease: Lease,
        payments: List[Payment],
        current_date: date = None
    ) -> Dict[str, Any]:
        """Compiles a complete, immutable financial status payload for a lease."""
        if current_date is None:
            current_date = date.today()

        total_due = 0.0
        total_paid = 0.0
        overdue_payments = []
        max_overdue_days = 0

        for p in payments:
            total_due += float(p.amount_due)
            total_paid += float(p.amount_paid)
            
            # Check if overdue
            if p.status in [PaymentStatus.OVERDUE, PaymentStatus.PENDING, PaymentStatus.PARTIALLY_PAID]:
                o_days = cls.calculate_overdue_days(p.due_date, lease.grace_period_days, current_date)
                if o_days > 0 or p.due_date < current_date:
                    unpaid_balance = float(p.amount_due) - float(p.amount_paid)
                    interest = cls.calculate_statutory_interest(
                        unpaid_balance, o_days, float(lease.interest_rate_pa)
                    )
                    overdue_payments.append({
                        "payment_id": str(p.id),
                        "due_date": p.due_date.isoformat(),
                        "amount_due": float(p.amount_due),
                        "amount_paid": float(p.amount_paid),
                        "unpaid_balance": round(unpaid_balance, 2),
                        "overdue_days": o_days,
                        "statutory_interest": interest,
                    })
                    if o_days > max_overdue_days:
                        max_overdue_days = o_days

        outstanding_arrears = round(max(0.0, total_due - total_paid), 2)
        total_interest = sum(item["statutory_interest"] for item in overdue_payments)

        return {
            "lease_id": str(lease.id),
            "monthly_rent": float(lease.monthly_rent),
            "deposit": float(lease.deposit),
            "service_charge": float(lease.service_charge),
            "grace_period_days": lease.grace_period_days,
            "annual_interest_rate": float(lease.interest_rate_pa),
            "total_amount_billed": round(total_due, 2),
            "total_amount_paid": round(total_paid, 2),
            "total_outstanding_arrears": outstanding_arrears,
            "total_statutory_interest_accrued": round(total_interest, 2),
            "grand_total_payable": round(outstanding_arrears + total_interest, 2),
            "overdue_count": len(overdue_payments),
            "max_overdue_days": max_overdue_days,
            "overdue_details": overdue_payments,
            "facts_generated_date": current_date.isoformat(),
        }
