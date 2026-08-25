from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.ai_service import explain_finding
from app.auth import get_current_user
from app.database import get_db
from app.deps import get_current_merchant
from app.models import (
    AuditLog,
    ComplianceCheck,
    ComplianceFinding,
    Merchant,
    PaymentConfiguration,
    User,
)
from app.rule_engine import run_rule_engine
from app.schemas import (
    AIExplanation,
    ComplianceCheckOut,
    ComplianceFindingOut,
    ExplainRequest,
    ResolveRequest,
    ScanRequest,
)

router = APIRouter(tags=["compliance"])


@router.post("/compliance/scan", response_model=ComplianceCheckOut)
def run_scan(
    payload: ScanRequest,
    merchant: Merchant = Depends(get_current_merchant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    config = (
        db.query(PaymentConfiguration)
        .filter(
            PaymentConfiguration.id == payload.payment_configuration_id,
            PaymentConfiguration.merchant_id == merchant.id,
        )
        .first()
    )
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")

    # 1. Deterministic rule engine is the ONLY thing that decides risk.
    result = run_rule_engine(config)

    check = ComplianceCheck(
        payment_configuration_id=config.id,
        merchant_id=merchant.id,
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        status="resolved" if not result.findings else "open",
        resolved_at=datetime.now(timezone.utc) if not result.findings else None,
    )
    db.add(check)
    db.flush()

    # 2. Each finding gets an AI-generated plain-language explanation --
    #    the AI never adds/changes/removes findings, it only explains them.
    for f in result.findings:
        ai_expl = explain_finding(f)
        finding_row = ComplianceFinding(
            compliance_check_id=check.id,
            rule_code=f.rule_code,
            severity=f.severity,
            reason=f.reason,
            suggested_action=f.suggested_action,
            field_name=f.field_name,
            ai_explanation=ai_expl,
        )
        db.add(finding_row)

    db.add(
        AuditLog(
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="SCAN_RUN",
            entity_type="compliance_check",
            entity_id=check.id,
            risk_level=result.risk_level,
            details={
                "payment_configuration_id": config.id,
                "findings_count": len(result.findings),
                "risk_score": result.risk_score,
            },
        )
    )
    db.commit()
    db.refresh(check)
    return check


@router.get("/compliance/findings", response_model=list[ComplianceFindingOut])
def list_findings(
    status_filter: str | None = None,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    query = (
        db.query(ComplianceFinding)
        .join(ComplianceCheck, ComplianceFinding.compliance_check_id == ComplianceCheck.id)
        .filter(ComplianceCheck.merchant_id == merchant.id)
    )
    if status_filter:
        query = query.filter(ComplianceCheck.status == status_filter)
    return query.order_by(ComplianceFinding.created_at.desc()).all()


@router.get("/compliance/history", response_model=list[ComplianceCheckOut])
def compliance_history(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    return (
        db.query(ComplianceCheck)
        .options(joinedload(ComplianceCheck.findings))
        .filter(ComplianceCheck.merchant_id == merchant.id)
        .order_by(ComplianceCheck.created_at.desc())
        .all()
    )


@router.post("/compliance/{check_id}/resolve", response_model=ComplianceCheckOut)
def resolve_check(
    check_id: str,
    payload: ResolveRequest,
    merchant: Merchant = Depends(get_current_merchant),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check = (
        db.query(ComplianceCheck)
        .filter(ComplianceCheck.id == check_id, ComplianceCheck.merchant_id == merchant.id)
        .first()
    )
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance check not found")

    check.status = "resolved"
    check.resolved_at = datetime.now(timezone.utc)

    db.add(
        AuditLog(
            merchant_id=merchant.id,
            user_id=current_user.id,
            action="CHECK_RESOLVED",
            entity_type="compliance_check",
            entity_id=check.id,
            risk_level=check.risk_level,
            details={"resolution_note": payload.resolution_note},
        )
    )
    db.commit()
    db.refresh(check)
    return check


@router.post("/ai/explain", response_model=AIExplanation)
def explain(
    payload: ExplainRequest,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    finding = (
        db.query(ComplianceFinding)
        .join(ComplianceCheck, ComplianceFinding.compliance_check_id == ComplianceCheck.id)
        .filter(ComplianceFinding.id == payload.finding_id, ComplianceCheck.merchant_id == merchant.id)
        .first()
    )
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    if finding.ai_explanation:
        return AIExplanation(**finding.ai_explanation)

    # Fallback: rebuild a Finding dataclass from the stored row and explain it
    from app.rule_engine import Finding as FindingDC

    dc = FindingDC(
        rule_code=finding.rule_code,
        severity=finding.severity,
        field_name=finding.field_name,
        reason=finding.reason,
        suggested_action=finding.suggested_action,
    )
    expl = explain_finding(dc)
    finding.ai_explanation = expl
    db.commit()
    return AIExplanation(**expl)
