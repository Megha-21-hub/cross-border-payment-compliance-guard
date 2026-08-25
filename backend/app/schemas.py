from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    merchant_id: Optional[str] = None

    class Config:
        from_attributes = True


class MerchantOut(BaseModel):
    id: str
    business_name: str
    business_type: str
    country: str
    default_iec_code: Optional[str] = None
    demo_persona: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Payment configurations
# ---------------------------------------------------------------------------
class PaymentConfigurationCreate(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3)
    amount: float = Field(..., gt=0)
    customer_country: Optional[str] = None
    payment_method: Optional[str] = "card"
    purpose_code: Optional[str] = None
    iec_code: Optional[str] = None
    hs_code: Optional[str] = None
    documentation_status: Optional[str] = "unknown"
    invoice_reference: Optional[str] = None
    # If true, backend will attempt a real Razorpay Test Mode order/payment call
    use_razorpay_test_api: bool = True


class PaymentConfigurationUpdate(BaseModel):
    purpose_code: Optional[str] = None
    iec_code: Optional[str] = None
    hs_code: Optional[str] = None
    documentation_status: Optional[str] = None
    invoice_reference: Optional[str] = None


class PaymentConfigurationOut(BaseModel):
    id: str
    merchant_id: str
    currency: str
    amount: float
    customer_country: Optional[str]
    payment_method: Optional[str]
    is_international: bool
    purpose_code: Optional[str]
    iec_code: Optional[str]
    hs_code: Optional[str]
    documentation_status: Optional[str]
    invoice_reference: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    transaction_data_source: str
    compliance_data_source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Compliance
# ---------------------------------------------------------------------------
class AIExplanation(BaseModel):
    summary: str
    why_it_matters: str
    recommended_action: str
    confidence: str
    mode: str  # "live_llm" | "demo_template"


class ComplianceFindingOut(BaseModel):
    id: str
    compliance_check_id: str
    rule_code: str
    severity: str
    reason: str
    suggested_action: str
    field_name: Optional[str]
    ai_explanation: Optional[dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceCheckOut(BaseModel):
    id: str
    payment_configuration_id: str
    merchant_id: str
    risk_level: str
    risk_score: int
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]
    findings: list[ComplianceFindingOut] = []

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    payment_configuration_id: str


class ResolveRequest(BaseModel):
    resolution_note: Optional[str] = None


class ExplainRequest(BaseModel):
    finding_id: str


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardSummary(BaseModel):
    total_configurations: int
    safe_configurations: int
    needs_review_configurations: int
    high_risk_configurations: int
    overall_compliance_score: int
    recent_checks: list[ComplianceCheckOut]
    demo_mode: dict[str, bool]


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
class AuditLogOut(BaseModel):
    id: str
    merchant_id: str
    user_id: Optional[str]
    action: str
    entity_type: str
    entity_id: str
    risk_level: Optional[str]
    details: Optional[dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
