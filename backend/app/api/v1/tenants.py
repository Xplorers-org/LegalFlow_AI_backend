import uuid
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.api.v1.auth import get_current_user
from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from backend.app.schemas.user import UserResponse
from backend.app.models.user import UserRole
from backend.app.core.logging import get_logger

router = APIRouter(prefix="/tenant", tags=["Tenants"])
logger = get_logger("backend.api.tenants")


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Creates a commercial tenant profile AND auto-provisions a tenant User account for login."""
    repo = TenantRepository(db)
    user_repo = UserRepository(db)

    # 1. Create Tenant Entity
    tenant = await repo.create(tenant_in.model_dump())

    # 2. Auto-provision Tenant User Login Account if not existing
    existing_user = await user_repo.get_by_email(tenant.email)
    temp_password = f"TenantPass_{secrets.token_hex(4)}"

    if not existing_user:
        hashed_pwd = get_password_hash(temp_password)
        await user_repo.create({
            "name": tenant.name,
            "email": tenant.email,
            "password_hash": hashed_pwd,
            "role": UserRole.TENANT,
            "phone": tenant.phone,
        })
        logger.info("Auto-provisioned login account for new tenant", email=tenant.email)
    else:
        temp_password = "ExistingAccountPassword"

    res = TenantResponse.model_validate(tenant)
    res.temp_password = temp_password
    return res


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
