from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_merchant
from app.models import AuditLog, Merchant, PaymentConfiguration, User
from app.auth import get_current_user
from app.razorpay_service import create_test_transaction
from app.schemas import (
    PaymentConfigurationCreate,
    PaymentConfigurationOut,
    PaymentConfigurationUpdate,
)

router = APIRouter(prefix="/payment-configurations", tags=["payment-configurations"])


@router.get("", response_model=list[PaymentConfigurationOut])
def list_configurations(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    return (
        db.query(PaymentConfiguration)
        .filter(PaymentConfiguration.merchant_id == merchant.id)
        .order_by(PaymentConfiguration.created_at.desc())
        .all()
    )


@router.get("/{config_id}", response_model=PaymentConfigurationOut)
def get_configuration(
    config_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    config = (
        db.query(PaymentConfiguration)
        .filter(PaymentConfiguration.id == config_id, PaymentConfiguration.merchant_id == merchant.id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return config


@router.post("", response_model=PaymentConfigurationOut, status_code=status.HTTP_201_CREATED)
def create_configuration(
    payload: PaymentConfigurationCreate,
    merchant: Merchant = Depends(get_current_merchant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    currency = payload.currency.upper()
    is_international = currency != "INR"

    razorpay_order_id = None
    razorpay_payment_id = None
    transaction_source = "manual_entry"

    if payload.use_razorpay_test_api:
        tx = create_test_transaction(
            currency=currency,
            amount=payload.amount,
            customer_country=payload.customer_country,
            payment_method=payload.payment_method,
            notes={"merchant": merchant.business_name},
        )
        razorpay_order_id = tx["order_id"]
        razorpay_payment_id = tx["payment_id"]
        is_international = tx["is_international"]
        transaction_source = tx["source"]

    config = PaymentConfiguration(
        merchant_id=merchant.id,
        currency=currency,
        amount=payload.amount,
        customer_country=payload.customer_country,
        payment_method=payload.payment_method,
        is_international=is_international,
        purpose_code=payload.purpose_code,
        iec_code=payload.iec_code,
        hs_code=payload.hs_code,
        documentation_status=payload.documentation_status or "unknown",
        invoice_reference=payload.invoice_reference,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        transaction_data_source=transaction_source,
        compliance_data_source="manual_entry",
    )
    db.add(config)
    db.flush()

    db.add(
        AuditLog(
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="CONFIG_CREATED",
            entity_type="payment_configuration",
            entity_id=config.id,
            details={"currency": currency, "amount": payload.amount, "source": transaction_source},
        )
    )
    db.commit()
    db.refresh(config)
    return config


@router.patch("/{config_id}", response_model=PaymentConfigurationOut)
def update_configuration(
    config_id: str,
    payload: PaymentConfigurationUpdate,
    merchant: Merchant = Depends(get_current_merchant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = (
        db.query(PaymentConfiguration)
        .filter(PaymentConfiguration.id == config_id, PaymentConfiguration.merchant_id == merchant.id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")

    changed_fields = {}
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(config, field_name, value)
            changed_fields[field_name] = value

    if changed_fields:
        config.compliance_data_source = "manual_entry"
        db.add(
            AuditLog(
                merchant_id=merchant.id,
                user_id=current_user.id,
                action="CONFIG_UPDATED",
                entity_type="payment_configuration",
                entity_id=config.id,
                details=changed_fields,
            )
        )

    db.commit()
    db.refresh(config)
    return config
