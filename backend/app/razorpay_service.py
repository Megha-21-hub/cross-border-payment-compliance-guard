"""
Razorpay Test Mode integration layer.

WHAT'S REAL vs SIMULATED (verified against Razorpay's official API docs):

  Real, API-fetchable fields on a Razorpay Order/Payment in Test Mode:
    - amount, currency, status, method, order_id, id (payment id)
    - "international": true/false  <-- a genuine field Razorpay returns
    - notes (custom key-value metadata we attach ourselves)

  NOT exposed via any Razorpay REST API (confirmed while researching this
  project -- these live only on the Razorpay Dashboard's "International
  Payment Codes" settings screen, which has no public fetch endpoint):
    - purpose_code, IEC code, HS code

  Because of this, this service only ever asks Razorpay to create/confirm
  the *transaction* itself (amount, currency, international flag). The
  compliance-profile fields (purpose code / IEC / HS code) always come from
  our own database, entered through our own UI -- and every record is
  labelled with its true `transaction_data_source` /
  `compliance_data_source` so nothing is presented as more "real" than it is.

MOCK FALLBACK:
  If RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET are not configured, this service
  returns a realistic simulated order/payment instead of calling the network,
  clearly tagged with DataSource.MOCK, so the app is always demoable.
"""
import random
import string
import time

import httpx

from app.config import settings
from app.models import DataSource

RAZORPAY_BASE_URL = "https://api.razorpay.com/v1"


def _random_id(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_letters + string.digits, k=14))
    return f"{prefix}_{suffix}"


def create_test_transaction(
    currency: str,
    amount: float,
    customer_country: str | None,
    payment_method: str | None,
    notes: dict | None = None,
) -> dict:
    """
    Attempts a real Razorpay Test Mode order creation call. Falls back to a
    clearly-labelled mock transaction if credentials are missing or the call
    fails for any reason (e.g. no network in this environment).

    Returns a dict with: order_id, payment_id, is_international, source
    """
    is_international = currency.upper() != "INR"

    if settings.razorpay_configured:
        try:
            amount_paise = int(round(amount * 100))
            with httpx.Client(
                base_url=RAZORPAY_BASE_URL,
                auth=(settings.razorpay_key_id, settings.razorpay_key_secret),
                timeout=10.0,
            ) as client:
                order_resp = client.post(
                    "/orders",
                    json={
                        "amount": amount_paise,
                        "currency": currency.upper(),
                        "notes": notes or {},
                    },
                )
                order_resp.raise_for_status()
                order_data = order_resp.json()

                return {
                    "order_id": order_data["id"],
                    # Test Mode orders aren't auto-paid; no live payment_id exists
                    # until a checkout actually happens, so we leave it unset.
                    "payment_id": None,
                    "is_international": is_international,
                    "source": DataSource.RAZORPAY_LIVE.value,
                }
        except Exception:
            # Network unavailable / bad credentials / API error -> fall back to mock.
            pass

    # ---- Mock fallback (clearly labelled) ----
    return {
        "order_id": _random_id("order"),
        "payment_id": _random_id("pay"),
        "is_international": is_international,
        "source": DataSource.MOCK.value,
    }
