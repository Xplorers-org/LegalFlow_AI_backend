import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.lease_repository import LeaseRepository
from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.schemas.lease import LeaseCreate, LeaseUpdate, LeaseResponse
from backend.app.schemas.user import UserResponse

router = APIRouter(prefix="/lease", tags=["Leases"])


@router.post("", response_model=LeaseResponse, status_code=status.HTTP_201_CREATED)
async def create_lease(
    lease_in: LeaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Creates a new commercial lease agreement."""
    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get(lease_in.tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant does not exist")

    repo = LeaseRepository(db)
    lease = await repo.create(lease_in.model_dump())
    return LeaseResponse.model_validate(lease)


@router.get("", response_model=List[LeaseResponse])
async def list_leases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves all commercial lease records."""
    repo = LeaseRepository(db)
    leases = await repo.get_all(skip=skip, limit=limit)
    return [LeaseResponse.model_validate(l) for l in leases]


@router.get("/{id}", response_model=LeaseResponse)
async def get_lease(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves a specific lease agreement by UUID."""
    repo = LeaseRepository(db)
    lease = await repo.get(id)
    if not lease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found")
    return LeaseResponse.model_validate(lease)


@router.put("/{id}", response_model=LeaseResponse)
async def update_lease(
    id: uuid.UUID,
    lease_in: LeaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Updates a commercial lease agreement."""
    repo = LeaseRepository(db)
    lease = await repo.update(id, lease_in.model_dump(exclude_unset=True))
    if not lease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found")
    return LeaseResponse.model_validate(lease)
