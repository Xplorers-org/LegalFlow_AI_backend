from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from backend.app.models.case import CaseStatus


class CaseBase(BaseModel):
    lease_id: UUID
    status: CaseStatus = CaseStatus.OPEN
    total_arrears: float = 0.0
    overdue_days: int = 0
    risk_score: str | None = None
    recommended_action: str | None = None
    ai_reasoning: str | None = None
    financial_facts_json: dict | None = None


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
