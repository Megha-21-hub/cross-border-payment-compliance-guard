from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.deps import get_current_merchant
from app.models import ComplianceCheck, Merchant, PaymentConfiguration
from app.schemas import DashboardSummary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    configs = (
        db.query(PaymentConfiguration)
        .filter(PaymentConfiguration.merchant_id == merchant.id)
        .all()
    )

    safe = 0
    needs_review = 0
    high_risk = 0
    score_accumulator = []

    for config in configs:
        latest_check = (
            db.query(ComplianceCheck)
            .filter(ComplianceCheck.payment_configuration_id == config.id)
            .order_by(ComplianceCheck.created_at.desc())
            .first()
        )
        if latest_check is None:
            needs_review += 1
            continue

        score_accumulator.append(latest_check.risk_score)

        if latest_check.risk_level == "high":
            high_risk += 1
        elif latest_check.risk_level == "low" and latest_check.status == "resolved":
            safe += 1
        else:
            needs_review += 1

    if score_accumulator:
        avg_risk = sum(score_accumulator) / len(score_accumulator)
        overall_score = max(0, round(100 - avg_risk))
    else:
        overall_score = 100

    recent_checks = (
        db.query(ComplianceCheck)
        .options(joinedload(ComplianceCheck.findings))
        .filter(ComplianceCheck.merchant_id == merchant.id)
        .order_by(ComplianceCheck.created_at.desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        total_configurations=len(configs),
        safe_configurations=safe,
        needs_review_configurations=needs_review,
        high_risk_configurations=high_risk,
        overall_compliance_score=overall_score,
        recent_checks=recent_checks,
        demo_mode={
            "razorpay_demo_mode": not settings.razorpay_configured,
            "ai_demo_mode": not settings.llm_configured,
        },
    )
