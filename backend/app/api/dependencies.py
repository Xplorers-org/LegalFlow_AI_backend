from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db

from backend.app.repositories.tenant_repository import TenantRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.lease_repository import LeaseRepository
from backend.app.repositories.payment_repository import PaymentRepository
from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.document_repository import DocumentRepository

def get_tenant_repository(db: AsyncSession = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_lease_repository(db: AsyncSession = Depends(get_db)) -> LeaseRepository:
    return LeaseRepository(db)

def get_payment_repository(db: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)

def get_case_repository(db: AsyncSession = Depends(get_db)) -> CaseRepository:
    return CaseRepository(db)

def get_document_repository(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)
