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
from backend.app.services.lease_parser import LeaseParserService

router = APIRouter(prefix="/lease", tags=["Leases"])


@router.post("/parse", response_model=dict)
async def parse_lease_agreement(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Parses an uploaded Lease Agreement PDF, extracts text, and queries Gemini
    via OpenRouter to extract schedules, utilities, and financial terms.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF lease agreements are supported."
        )

    try:
        pdf_bytes = await file.read()
        extracted_text = LeaseParserService.extract_text_from_pdf(pdf_bytes)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The uploaded PDF does not contain extractable text content."
            )

        parsed_data = LeaseParserService.parse_lease_text(extracted_text)
        return parsed_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse lease agreement: {str(e)}"
        )


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
