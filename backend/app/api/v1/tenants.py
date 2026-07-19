import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from backend.app.schemas.user import UserResponse

router = APIRouter(prefix="/tenant", tags=["Tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Creates a new commercial tenant record."""
    repo = TenantRepository(db)
    tenant = await repo.create(tenant_in.model_dump())
    return TenantResponse.model_validate(tenant)


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves all commercial tenants."""
    repo = TenantRepository(db)
    tenants = await repo.get_all(skip=skip, limit=limit)
    return [TenantResponse.model_validate(t) for t in tenants]


@router.get("/{id}", response_model=TenantResponse)
async def get_tenant(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves a specific tenant by UUID."""
    repo = TenantRepository(db)
    tenant = await repo.get(id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantResponse.model_validate(tenant)


@router.put("/{id}", response_model=TenantResponse)
async def update_tenant(
    id: uuid.UUID,
    tenant_in: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Updates a tenant record."""
    repo = TenantRepository(db)
    tenant = await repo.update(id, tenant_in.model_dump(exclude_unset=True))
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantResponse.model_validate(tenant)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Deletes a tenant record."""
    repo = TenantRepository(db)
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
