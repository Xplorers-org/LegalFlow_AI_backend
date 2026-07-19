from datetime import date, timedelta
from backend.app.services.financial_engine import FinancialEngine
from backend.app.models.lease import Lease
from backend.app.models.payment import Payment, PaymentStatus


def test_calculate_overdue_days():
    due = date.today() - timedelta(days=20)
    # 20 days past due - 5 days grace period = 15 effective overdue days
    overdue_days = FinancialEngine.calculate_overdue_days(due, grace_period_days=5)
    assert overdue_days == 15


def test_calculate_statutory_interest():
    principal = 100000.0  # LKR 100,000
    overdue_days = 365
    annual_rate = 12.0  # 12% p.a.
    interest = FinancialEngine.calculate_statutory_interest(principal, overdue_days, annual_rate)
    assert interest == 12000.0  # LKR 12,000 exact annual interest


def test_compile_financial_facts():
    lease = Lease(
        monthly_rent=150000.0,
        deposit=300000.0,
        service_charge=15000.0,
        grace_period_days=5,
        interest_rate_pa=12.0,
    )
    p1 = Payment(
        amount_due=150000.0,
        amount_paid=0.0,
        due_date=date.today() - timedelta(days=30),
        status=PaymentStatus.OVERDUE
    )

    facts = FinancialEngine.compile_financial_facts(lease, [p1])
    assert facts["total_outstanding_arrears"] == 150000.0
    assert facts["overdue_count"] == 1
    assert facts["max_overdue_days"] == 25
    assert facts["total_statutory_interest_accrued"] > 0
