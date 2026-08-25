"""
AI Explanation Service.

PRODUCT PRINCIPLE (do not violate this):
  This module NEVER decides whether a risk exists. It only takes a finding
  that the deterministic rule_engine.py has already produced and:
    1. Rewrites the reason in simple, merchant-friendly language.
    2. Explains why it matters.
    3. Restates the recommended action in plain language.

  It must never use the words "illegal", "non-compliant", or "guaranteed
  compliant" -- only "potential risk", "requires review", "may need
  attention". This constraint is enforced both in the prompt AND by never
  letting the LLM freelance beyond the finding it was given.

DEMO MODE:
  If no LLM_API_KEY is configured, `explain_finding` falls back to a
  deterministic template per rule_code, so the product is always fully
  demoable. The returned dict always includes `"mode"` so the frontend can
  show a "Demo AI" badge when appropriate.
"""
import httpx

from app.config import settings
from app.rule_engine import Finding

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """You are a plain-language explainer for a fintech compliance-review tool used \
by Indian merchants accepting international payments.

You will be given ONE finding that a deterministic rule engine already raised. You do not decide \
whether risk exists -- that has already been decided. Your only job is to explain it clearly.

Rules you must always follow:
- Never say "illegal", "non-compliant", or "guaranteed compliant".
- Only use phrases like "potential risk", "requires review", "may need attention", "missing information".
- Do not invent any RBI, FEMA, GST, or Razorpay rule beyond what is given to you in the finding.
- Keep language simple enough for a non-lawyer founder to understand in a few seconds.
- Respond ONLY with a JSON object, no markdown fences, no preamble, with exactly these keys:
  "summary" (one sentence, what was found),
  "why_it_matters" (one to two sentences, plain language),
  "recommended_action" (one sentence, concrete next step),
  "confidence" (one of: "high", "medium", "low" -- how confident the explanation is given the data provided)
"""

# ---------------------------------------------------------------------------
# Demo-mode deterministic templates (no LLM key required)
# ---------------------------------------------------------------------------
_DEMO_TEMPLATES: dict[str, dict[str, str]] = {
    "PURPOSE_CODE_MISSING": {
        "summary": "This international transaction doesn't have a purpose code attached yet.",
        "why_it_matters": "Purpose codes tell banks and regulators what an international payment is for. Without one, the payment's paperwork (like a FIRC/FIRS certificate) may be delayed or incorrect later.",
        "recommended_action": "Open the transaction and select the RBI purpose code that best matches what was sold (e.g. software services).",
        "confidence": "high",
    },
    "PURPOSE_CODE_DIRECTION_MISMATCH": {
        "summary": "The purpose code on this transaction looks like it's meant for outgoing payments, not incoming ones.",
        "why_it_matters": "Since your business is receiving money from abroad, the purpose code should typically be an export-type code. A mismatched code can cause confusion in your compliance paperwork.",
        "recommended_action": "Double check the transaction direction and update the purpose code to an export ('P'-prefixed) code if this is revenue you're receiving.",
        "confidence": "medium",
    },
    "PURPOSE_CODE_FORMAT_UNRECOGNISED": {
        "summary": "The purpose code entered doesn't match the usual format banks expect.",
        "why_it_matters": "An unusual-looking code is worth a second look so it doesn't get rejected or questioned later.",
        "recommended_action": "Compare this code against the official RBI purpose code list and correct it if needed.",
        "confidence": "medium",
    },
    "IEC_CODE_MISSING": {
        "summary": "No Import-Export Code (IEC) is on file for this transaction.",
        "why_it_matters": "Many international transactions expect an IEC on record for the business. Missing it can hold up documentation later.",
        "recommended_action": "Confirm whether your business needs an IEC for this transaction type, and add it if so.",
        "confidence": "medium",
    },
    "HS_CODE_MISSING": {
        "summary": "This transaction doesn't have an HS classification code recorded.",
        "why_it_matters": "HS codes classify exactly what's being sold internationally, which customs and compliance checks may reference.",
        "recommended_action": "Add the HS code that best matches the product or service in this transaction.",
        "confidence": "low",
    },
    "DOCUMENTATION_INCOMPLETE": {
        "summary": "Supporting documentation for this transaction looks incomplete or hasn't been confirmed.",
        "why_it_matters": "Incomplete paperwork now often means a scramble later when a bank or auditor asks for proof of the transaction.",
        "recommended_action": "Review and upload/confirm the invoice and any other supporting documents for this transaction.",
        "confidence": "medium",
    },
    "INVOICE_REFERENCE_MISSING": {
        "summary": "No invoice reference is linked to this transaction.",
        "why_it_matters": "An invoice reference makes it much easier to match this payment to your records later, including for FIRC/FIRS purposes.",
        "recommended_action": "Attach the invoice number associated with this payment.",
        "confidence": "low",
    },
    "CURRENCY_COUNTRY_SOFT_MISMATCH": {
        "summary": "The payment currency and the customer's listed country don't obviously match.",
        "why_it_matters": "This is often completely normal (for example, a marketplace paying on a customer's behalf), but it's worth a quick sanity check.",
        "recommended_action": "Confirm the customer's country and currency are correctly recorded.",
        "confidence": "low",
    },
    "HIGH_VALUE_UNVERIFIED": {
        "summary": "This is a larger transaction that's still missing its purpose code.",
        "why_it_matters": "The bigger the transaction, the more it matters to have accurate paperwork in place before money settles.",
        "recommended_action": "Prioritise adding a purpose code to this transaction before it proceeds further.",
        "confidence": "high",
    },
}

_DEFAULT_TEMPLATE = {
    "summary": "A potential configuration issue was found on this transaction.",
    "why_it_matters": "Incomplete configuration can slow down downstream compliance paperwork.",
    "recommended_action": "Review the flagged field and update it as needed.",
    "confidence": "low",
}


def _demo_explanation(finding: Finding) -> dict:
    template = _DEMO_TEMPLATES.get(finding.rule_code, _DEFAULT_TEMPLATE)
    return {
        "summary": template["summary"],
        "why_it_matters": template["why_it_matters"],
        "recommended_action": template["recommended_action"],
        "confidence": template["confidence"],
        "mode": "demo_template",
    }


def _call_llm(finding: Finding) -> dict | None:
    """Calls the Anthropic API. Returns None on any failure so callers can
    gracefully fall back to demo mode rather than breaking the scan."""
    if not settings.llm_configured:
        return None

    user_message = (
        f"Finding rule code: {finding.rule_code}\n"
        f"Severity (already decided by rule engine): {finding.severity}\n"
        f"Deterministic reason: {finding.reason}\n"
        f"Deterministic suggested action: {finding.suggested_action}\n\n"
        "Explain this finding to the merchant per your instructions."
    )

    try:
        response = httpx.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": settings.llm_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "max_tokens": 400,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        raw_text = "".join(text_blocks).strip()
        raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        import json

        parsed = json.loads(raw_text)
        return {
            "summary": parsed["summary"],
            "why_it_matters": parsed["why_it_matters"],
            "recommended_action": parsed["recommended_action"],
            "confidence": parsed.get("confidence", "medium"),
            "mode": "live_llm",
        }
    except Exception:
        # Any network/parsing failure silently falls back to demo mode --
        # the product must never break because the LLM had a bad moment.
        return None


def explain_finding(finding: Finding) -> dict:
    """Public entry point used by the compliance router."""
    live = _call_llm(finding)
    if live is not None:
        return live
    return _demo_explanation(finding)
