import uuid
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash
from backend.app.api.v1.auth import get_current_user
from backend.app.api.dependencies import get_tenant_repository, get_user_repository
from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from backend.app.schemas.user import UserResponse
from backend.app.models.user import UserRole
from backend.app.services.email_service import send_tenant_onboarding_email
from backend.app.core.logging import get_logger

router = APIRouter(prefix="/tenant", tags=["Tenants"])
logger = get_logger("backend.api.tenants")


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    repo: TenantRepository = Depends(get_tenant_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Creates a commercial tenant profile AND auto-provisions a tenant User account for login."""
    # 1. Create Tenant Entity
    tenant = await repo.create(tenant_in.model_dump())

    # 2. Auto-provision or update Tenant User Login Account
    existing_user = await user_repo.get_by_email(tenant.email)
    temp_password = f"TenantPass_{secrets.token_hex(4)}"
    hashed_pwd = get_password_hash(temp_password)

    if not existing_user:
        await user_repo.create({
            "name": tenant.name,
            "email": tenant.email,
            "password_hash": hashed_pwd,
            "role": UserRole.TENANT,
            "phone": tenant.phone,
        })
        logger.info("Auto-provisioned login account for new tenant", email=tenant.email)
    else:
        # If user exists (e.g. from prior tests), reset password and sync details
        await user_repo.update(existing_user.id, {
            "password_hash": hashed_pwd,
            "name": tenant.name,
            "phone": tenant.phone,
        })
        logger.info("Reset login account password for existing tenant user", email=tenant.email)

    # 3. Schedule automated onboarding email to tenant in background (Always send for seamless testing)
    background_tasks.add_task(
        send_tenant_onboarding_email,
        tenant_name=tenant.name,
        tenant_email=tenant.email,
        temp_password=temp_password,
        company=tenant.company,
    )

    # Commit synchronously to prevent race condition with subsequent lease creation request
    await db.commit()

    res = TenantResponse.model_validate(tenant)
    res.temp_password = temp_password
    return res


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    repo: TenantRepository = Depends(get_tenant_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves all commercial tenants."""
    tenants = await repo.get_all(skip=skip, limit=limit)
    return [TenantResponse.model_validate(t) for t in tenants]


@router.get("/{id}", response_model=TenantResponse)
async def get_tenant(
    id: uuid.UUID,
    repo: TenantRepository = Depends(get_tenant_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieves a specific tenant by UUID."""
    tenant = await repo.get(id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantResponse.model_validate(tenant)


@router.put("/{id}", response_model=TenantResponse)
async def update_tenant(
    id: uuid.UUID,
    tenant_in: TenantUpdate,
    repo: TenantRepository = Depends(get_tenant_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Updates a tenant record."""
    tenant = await repo.update(id, tenant_in.model_dump(exclude_unset=True))
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return TenantResponse.model_validate(tenant)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    id: uuid.UUID,
    repo: TenantRepository = Depends(get_tenant_repository),
    current_user: UserResponse = Depends(get_current_user),
):
    """Deletes a tenant record."""
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
