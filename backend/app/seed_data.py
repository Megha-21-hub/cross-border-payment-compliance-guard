"""
Seeds the database with demo users, merchants, and starter payment
configurations so the app is immediately demoable (per the project's
"demo mode with realistic sample merchants" requirement).

Idempotent: only seeds if the users table is empty.
"""
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import Merchant, PaymentConfiguration, User

DEMO_PASSWORD = "demo1234"


def seed_if_empty(db: Session) -> None:
    if db.query(User).first() is not None:
        return  # already seeded

    # ---- Merchant 1: TechNova Solutions -> US customer (the flagship demo) --
    technova = Merchant(
        business_name="TechNova Solutions",
        business_type="Software Services",
        country="India",
        default_iec_code=None,
        demo_persona="technova",
    )
    db.add(technova)
    db.flush()

    db.add(
        User(
            email="demo@technova.io",
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Aisha Rao",
            merchant_id=technova.id,
        )
    )
    db.add(
        PaymentConfiguration(
            merchant_id=technova.id,
            currency="USD",
            amount=1000.00,
            customer_country="United States",
            payment_method="card",
            is_international=True,
            purpose_code=None,
            iec_code=None,
            hs_code=None,
            documentation_status="incomplete",
            invoice_reference=None,
            razorpay_order_id="order_demoTechNova001",
            razorpay_payment_id="pay_demoTechNova001",
            transaction_data_source="mock_simulated",
            compliance_data_source="manual_entry",
        )
    )

    # ---- Merchant 2: Kavya Consulting -> UK customer (mostly clean) --------
    kavya = Merchant(
        business_name="Kavya Consulting",
        business_type="IT Consulting",
        country="India",
        default_iec_code="AABCK1234L",
        demo_persona="kavya_consulting",
    )
    db.add(kavya)
    db.flush()

    db.add(
        User(
            email="demo@kavyaconsulting.in",
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Kavya Menon",
            merchant_id=kavya.id,
        )
    )
    db.add(
        PaymentConfiguration(
            merchant_id=kavya.id,
            currency="GBP",
            amount=2500.00,
            customer_country="United Kingdom",
            payment_method="card",
            is_international=True,
            purpose_code="P0802",
            iec_code="AABCK1234L",
            hs_code="998313",
            documentation_status="complete",
            invoice_reference="INV-2201",
            razorpay_order_id="order_demoKavya001",
            razorpay_payment_id="pay_demoKavya001",
            transaction_data_source="mock_simulated",
            compliance_data_source="manual_entry",
        )
    )

    # ---- Merchant 3: Bloom Digital Agency -> Singapore customer (higher risk) --
    bloom = Merchant(
        business_name="Bloom Digital Agency",
        business_type="Digital Marketing",
        country="India",
        default_iec_code=None,
        demo_persona="bloom_digital",
    )
    db.add(bloom)
    db.flush()

    db.add(
        User(
            email="demo@bloomdigital.in",
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Rohan Iyer",
            merchant_id=bloom.id,
        )
    )
    db.add(
        PaymentConfiguration(
            merchant_id=bloom.id,
            currency="SGD",
            amount=4200.00,
            customer_country="Singapore",
            payment_method="card",
            is_international=True,
            purpose_code="S0703",  # deliberately wrong direction -> triggers high-severity finding
            iec_code=None,
            hs_code=None,
            documentation_status="unknown",
            invoice_reference=None,
            razorpay_order_id="order_demoBloom001",
            razorpay_payment_id="pay_demoBloom001",
            transaction_data_source="mock_simulated",
            compliance_data_source="manual_entry",
        )
    )

    db.commit()
