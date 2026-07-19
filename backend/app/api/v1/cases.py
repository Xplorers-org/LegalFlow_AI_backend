import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.case_repository import CaseRepository
from backend.app.schemas.case import CaseResponse
from backend.app.schemas.user import UserResponse

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    lease_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves compliance cases for commercial leases."""
    repo = CaseRepository(db)
    if lease_id:
        cases = await repo.get_by_lease(lease_id)
    else:
        cases = await repo.get_all(skip=skip, limit=limit)
    return [CaseResponse.model_validate(c) for c in cases]


@router.get("/{id}", response_model=CaseResponse)
async def get_case(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves details for a specific compliance case."""
    repo = CaseRepository(db)
    case = await repo.get(id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return CaseResponse.model_validate(case)
