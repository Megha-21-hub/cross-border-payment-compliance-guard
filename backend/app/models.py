import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CheckStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class DataSource(str, enum.Enum):
    RAZORPAY_LIVE = "razorpay_test_api"   # real call to Razorpay Test Mode
    MOCK = "mock_simulated"               # simulated / not available via API
    MANUAL = "manual_entry"               # merchant typed it into our form


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    created_at = Column(DateTime, default=_now)

    merchant = relationship("Merchant", back_populates="users")


# ---------------------------------------------------------------------------
# merchants
# ---------------------------------------------------------------------------
class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=_uid)
    business_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)   # e.g. "Software Services"
    country = Column(String, default="India")
    default_iec_code = Column(String, nullable=True)
    demo_persona = Column(String, nullable=True)      # tags seeded demo merchants
    created_at = Column(DateTime, default=_now)

    users = relationship("User", back_populates="merchant")
    payment_configurations = relationship("PaymentConfiguration", back_populates="merchant")
    audit_logs = relationship("AuditLog", back_populates="merchant")


# ---------------------------------------------------------------------------
# payment_configurations
# ---------------------------------------------------------------------------
class PaymentConfiguration(Base):
    __tablename__ = "payment_configurations"

    id = Column(String, primary_key=True, default=_uid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    # Transaction-level fields
    currency = Column(String, nullable=False)               # ISO code, e.g. USD
    amount = Column(Float, nullable=False)                   # major units (e.g. 1000.00)
    customer_country = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    is_international = Column(Boolean, default=True)

    # Compliance-profile fields (mostly simulated -- see DataSource)
    purpose_code = Column(String, nullable=True)
    iec_code = Column(String, nullable=True)
    hs_code = Column(String, nullable=True)
    documentation_status = Column(String, nullable=True)     # "complete" | "incomplete" | "unknown"
    invoice_reference = Column(String, nullable=True)

    # Provenance -- which fields were real vs simulated, kept transparent
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    transaction_data_source = Column(String, default=DataSource.MOCK.value)
    compliance_data_source = Column(String, default=DataSource.MANUAL.value)

    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    merchant = relationship("Merchant", back_populates="payment_configurations")
    compliance_checks = relationship("ComplianceCheck", back_populates="payment_configuration")


# ---------------------------------------------------------------------------
# compliance_checks  (one scan run)
# ---------------------------------------------------------------------------
class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(String, primary_key=True, default=_uid)
    payment_configuration_id = Column(String, ForeignKey("payment_configurations.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    risk_level = Column(String, default=RiskLevel.LOW.value)
    risk_score = Column(Integer, default=0)   # 0-100
    status = Column(String, default=CheckStatus.OPEN.value)

    created_at = Column(DateTime, default=_now)
    resolved_at = Column(DateTime, nullable=True)

    payment_configuration = relationship("PaymentConfiguration", back_populates="compliance_checks")
    findings = relationship("ComplianceFinding", back_populates="compliance_check", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# compliance_findings (one rule-engine flag within a check)
# ---------------------------------------------------------------------------
class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"

    id = Column(String, primary_key=True, default=_uid)
    compliance_check_id = Column(String, ForeignKey("compliance_checks.id"), nullable=False)

    rule_code = Column(String, nullable=False)         # e.g. "PURPOSE_CODE_MISSING"
    severity = Column(String, nullable=False)          # low | medium | high
    reason = Column(Text, nullable=False)              # deterministic, from rule engine
    suggested_action = Column(Text, nullable=False)     # deterministic, from rule engine
    field_name = Column(String, nullable=True)

    ai_explanation = Column(JSON, nullable=True)        # {summary, why_it_matters, next_step, confidence, mode}

    created_at = Column(DateTime, default=_now)

    compliance_check = relationship("ComplianceCheck", back_populates="findings")


# ---------------------------------------------------------------------------
# audit_logs
# ---------------------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_uid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    action = Column(String, nullable=False)             # SCAN_RUN | FINDING_RAISED | CONFIG_UPDATED | FINDING_RESOLVED
    entity_type = Column(String, nullable=False)         # payment_configuration | compliance_check | compliance_finding
    entity_id = Column(String, nullable=False)

    risk_level = Column(String, nullable=True)
    details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=_now)

    merchant = relationship("Merchant", back_populates="audit_logs")
