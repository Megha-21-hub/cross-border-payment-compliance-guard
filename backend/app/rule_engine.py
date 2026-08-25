"""
Deterministic Compliance Rule Engine.

PRODUCT PRINCIPLE (do not violate this):
  The rule engine is the ONLY component that decides whether a potential
  compliance/configuration risk exists. It never calls an LLM. It never
  invents a rule. Every finding it raises maps to a plain, hard-coded,
  explainable condition on the data already stored in `payment_configurations`.

  The AI layer (see ai_service.py) is only allowed to *explain* a finding
  this engine already produced -- it cannot add, remove, or reinterpret
  findings.

  This module deliberately never uses words like "illegal" or
  "non-compliant". Every finding is phrased as a *potential risk requiring
  review*, per the project's compliance-safe language requirement.
"""
from dataclasses import dataclass, field

from app.models import PaymentConfiguration

# Purpose codes: RBI convention is that export (inbound-to-India) codes start
# with 'P' and import (outbound-from-India) codes start with 'S'.
# Reference: Razorpay Purpose Codes documentation.
EXPORT_PREFIX = "P"
IMPORT_PREFIX = "S"

# A minimal, illustrative currency -> plausible-country lookup used only for
# a soft "does this look consistent" nudge. This is NOT an authoritative
# FEMA/RBI source and is intentionally limited -- if we don't recognise the
# pairing we simply skip the check rather than guessing.
CURRENCY_COUNTRY_HINTS = {
    "USD": {"united states", "usa", "us"},
    "GBP": {"united kingdom", "uk", "great britain"},
    "EUR": {"germany", "france", "spain", "italy", "netherlands", "ireland", "portugal"},
    "SGD": {"singapore"},
    "AUD": {"australia"},
    "CAD": {"canada"},
    "AED": {"united arab emirates", "uae"},
    "JPY": {"japan"},
}

HIGH_VALUE_THRESHOLD_USD_EQUIVALENT = 10_000  # illustrative demo threshold only

SEVERITY_POINTS = {"low": 10, "medium": 30, "high": 50}


@dataclass
class Finding:
    rule_code: str
    severity: str  # low | medium | high
    field_name: str | None
    reason: str
    suggested_action: str


@dataclass
class ScanResult:
    findings: list[Finding] = field(default_factory=list)
    risk_score: int = 0
    risk_level: str = "low"


def _norm(value: str | None) -> str:
    return (value or "").strip()


def run_rule_engine(config: PaymentConfiguration) -> ScanResult:
    findings: list[Finding] = []

    purpose_code = _norm(config.purpose_code)
    iec_code = _norm(config.iec_code)
    hs_code = _norm(config.hs_code)
    doc_status = _norm(config.documentation_status).lower()
    invoice_ref = _norm(config.invoice_reference)
    currency = _norm(config.currency).upper()
    customer_country = _norm(config.customer_country).lower()

    # --- RULE 1: Purpose code missing -------------------------------------
    if config.is_international and not purpose_code:
        findings.append(
            Finding(
                rule_code="PURPOSE_CODE_MISSING",
                severity="medium",
                field_name="purpose_code",
                reason="Purpose-code information is missing for an international transaction.",
                suggested_action="Review and select the appropriate RBI purpose code before proceeding.",
            )
        )

    # --- RULE 2: Purpose code direction mismatch ---------------------------
    # This app models inbound remittances (Indian merchant receiving foreign
    # payment) -- so a correctly-set purpose code should be an export ('P')
    # code, not an import ('S') code.
    if purpose_code and config.is_international:
        first_letter = purpose_code[:1].upper()
        if first_letter == IMPORT_PREFIX:
            findings.append(
                Finding(
                    rule_code="PURPOSE_CODE_DIRECTION_MISMATCH",
                    severity="high",
                    field_name="purpose_code",
                    reason=(
                        f"Purpose code '{purpose_code}' begins with '{IMPORT_PREFIX}', which is "
                        "conventionally used for outward (import) remittances, but this transaction "
                        "is an inbound payment received by the merchant."
                    ),
                    suggested_action="Confirm the transaction direction and select an export ('P'-prefixed) purpose code if this is inbound revenue.",
                )
            )
        elif first_letter != EXPORT_PREFIX:
            findings.append(
                Finding(
                    rule_code="PURPOSE_CODE_FORMAT_UNRECOGNISED",
                    severity="low",
                    field_name="purpose_code",
                    reason=f"Purpose code '{purpose_code}' does not follow the expected P/S prefix convention.",
                    suggested_action="Double-check the purpose code against the RBI purpose code list.",
                )
            )

    # --- RULE 3: IEC missing for a business type that typically needs one --
    if config.is_international and not iec_code:
        findings.append(
            Finding(
                rule_code="IEC_CODE_MISSING",
                severity="medium",
                field_name="iec_code",
                reason="No Importer-Exporter Code (IEC) is on record for this merchant's international transaction.",
                suggested_action="Confirm whether an IEC is required for this business type and add it if so.",
            )
        )

    # --- RULE 4: HS code missing --------------------------------------------
    if config.is_international and not hs_code:
        findings.append(
            Finding(
                rule_code="HS_CODE_MISSING",
                severity="low",
                field_name="hs_code",
                reason="No HS (Harmonised System) classification code is recorded for this transaction.",
                suggested_action="Add the HS code that best classifies the goods/services being provided.",
            )
        )

    # --- RULE 5: Documentation incomplete -----------------------------------
    if doc_status in {"incomplete", "unknown", ""}:
        findings.append(
            Finding(
                rule_code="DOCUMENTATION_INCOMPLETE",
                severity="medium" if doc_status == "incomplete" else "low",
                field_name="documentation_status",
                reason="Supporting documentation status for this transaction is marked incomplete or unknown.",
                suggested_action="Upload/confirm invoice and supporting export documentation for this transaction.",
            )
        )

    # --- RULE 6: Missing invoice reference -----------------------------------
    if not invoice_ref:
        findings.append(
            Finding(
                rule_code="INVOICE_REFERENCE_MISSING",
                severity="low",
                field_name="invoice_reference",
                reason="No invoice reference number is linked to this transaction.",
                suggested_action="Attach an invoice reference for traceability and future FIRC/FIRS matching.",
            )
        )

    # --- RULE 7: Currency / customer-country soft consistency check --------
    if currency in CURRENCY_COUNTRY_HINTS and customer_country:
        expected = CURRENCY_COUNTRY_HINTS[currency]
        if not any(hint in customer_country or customer_country in hint for hint in expected):
            findings.append(
                Finding(
                    rule_code="CURRENCY_COUNTRY_SOFT_MISMATCH",
                    severity="low",
                    field_name="customer_country",
                    reason=(
                        f"Currency '{currency}' is not typically associated with customer country "
                        f"'{config.customer_country}'. This may be entirely normal (e.g. a marketplace "
                        "or intermediary payer) but is worth a quick check."
                    ),
                    suggested_action="Confirm the customer's billing country matches the transaction currency.",
                )
            )

    # --- RULE 8: High-value transaction with missing purpose code ----------
    # Escalates rule 1 rather than duplicating it.
    if config.is_international and not purpose_code and config.amount >= HIGH_VALUE_THRESHOLD_USD_EQUIVALENT:
        findings.append(
            Finding(
                rule_code="HIGH_VALUE_UNVERIFIED",
                severity="high",
                field_name="amount",
                reason=(
                    f"This is a high-value transaction ({config.currency} {config.amount:,.2f}) with no "
                    "purpose code on record, which increases the potential impact of a configuration gap."
                ),
                suggested_action="Prioritise reviewing this transaction's purpose code before settlement.",
            )
        )

    result = _score(findings)
    return result


def _score(findings: list[Finding]) -> ScanResult:
    score = 0
    has_high = False
    for f in findings:
        score += SEVERITY_POINTS.get(f.severity, 0)
        if f.severity == "high":
            has_high = True
    score = min(score, 100)

    if has_high or score >= 70:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return ScanResult(findings=findings, risk_score=score, risk_level=level)
