from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Merchant, User


def get_current_merchant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Merchant:
    if not current_user.merchant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is not linked to a merchant account.",
        )
    merchant = db.query(Merchant).filter(Merchant.id == current_user.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")
    return merchant
