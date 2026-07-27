import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from backend.app.core.database import get_db

router = APIRouter(prefix="/utility-bills", tags=["Utility Bills"])

# Pydantic Schemas
class UtilityBillCreate(BaseModel):
    account_number: str
    utility_type: str  # 'ELECTRICITY' or 'WATER'
    amount: float
    due_date: date

class UtilityBillReconcile(BaseModel):
    account_number: str
    utility_type: str

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_utility_bill(
    bill_in: UtilityBillCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new utility bill by matching the account number to a tenant lease."""
    # Find matching lease and get the tenant's email address
    find_lease_sql = text("""
        SELECT l.id, t.email FROM leases l
        JOIN tenants t ON l.tenant_id = t.id
        WHERE (l.extracted_metadata->'third_schedule_utilities'->>'electricity_account_no' = :acc_num)
           OR (l.extracted_metadata->'third_schedule_utilities'->>'water_account_no' = :acc_num)
        LIMIT 1;
    """)
    res = await db.execute(find_lease_sql, {"acc_num": bill_in.account_number})
    row = res.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No active lease matches account number {bill_in.account_number}"
        )
    
    lease_id = row[0]
    tenant_email = row[1]
    
    # Insert utility bill
    insert_sql = text("""
        INSERT INTO utility_bills (id, lease_id, utility_type, account_number, amount, due_date, status, created_at, updated_at)
        VALUES (gen_random_uuid(), :lease_id, :utility_type, :account_number, :amount, :due_date, 'PENDING', NOW(), NOW())
        RETURNING id, lease_id, utility_type, account_number, amount, due_date, status, created_at, updated_at;
    """)
    insert_res = await db.execute(insert_sql, {
        "lease_id": lease_id,
        "utility_type": bill_in.utility_type.upper(),
        "account_number": bill_in.account_number,
        "amount": bill_in.amount,
        "due_date": bill_in.due_date
    })
    new_row = insert_res.first()
    await db.commit()
    
    return {
        "id": new_row[0],
        "lease_id": new_row[1],
        "utility_type": new_row[2],
        "account_number": new_row[3],
        "amount": float(new_row[4]),
        "due_date": new_row[5].isoformat(),
        "status": new_row[6],
        "created_at": new_row[7].isoformat(),
        "updated_at": new_row[8].isoformat(),
        "tenant_email": tenant_email
    }

@router.post("/reconcile", status_code=status.HTTP_200_OK)
async def reconcile_utility_bill(
    reconcile_in: UtilityBillReconcile,
    db: AsyncSession = Depends(get_db)
):
    """Marks pending utility bills as PAID for the specified account number."""
    update_sql = text("""
        UPDATE utility_bills 
        SET status = 'PAID', updated_at = NOW()
        WHERE account_number = :acc_num AND status = 'PENDING' AND utility_type = :util_type
        RETURNING id;
    """)
    res = await db.execute(update_sql, {
        "acc_num": reconcile_in.account_number,
        "util_type": reconcile_in.utility_type.upper()
    })
    rows = res.all()
    await db.commit()
    
    return {
        "success": True,
        "reconciled_count": len(rows),
        "bill_ids": [r[0] for r in rows]
    }

@router.get("", status_code=status.HTTP_200_OK)
async def list_utility_bills(
    lease_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all utility bills, optionally filtered by lease ID."""
    if lease_id:
        query = text("""
            SELECT id, lease_id, utility_type, account_number, amount, due_date, status, created_at, updated_at
            FROM utility_bills
            WHERE lease_id = :lease_id
            ORDER BY due_date DESC;
        """)
        res = await db.execute(query, {"lease_id": lease_id})
    else:
        query = text("""
            SELECT id, lease_id, utility_type, account_number, amount, due_date, status, created_at, updated_at
            FROM utility_bills
            ORDER BY due_date DESC;
        """)
        res = await db.execute(query)
        
    rows = res.all()
    return [
        {
            "id": r[0],
            "lease_id": r[1],
            "utility_type": r[2],
            "account_number": r[3],
            "amount": float(r[4]),
            "due_date": r[5].isoformat(),
            "status": r[6],
            "created_at": r[7].isoformat(),
            "updated_at": r[8].isoformat()
        }
        for r in rows
    ]
