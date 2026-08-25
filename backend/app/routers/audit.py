from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_merchant
from app.models import AuditLog, Merchant
from app.schemas import AuditLogOut

router = APIRouter(tags=["audit"])


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
    limit: int = 100,
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.merchant_id == merchant.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
