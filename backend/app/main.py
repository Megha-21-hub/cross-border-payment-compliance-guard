from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, compliance, dashboard, payment_configs, audit
from app.seed_data import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and seed demo data on startup.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Cross-Border Payment Compliance Guard",
    description=(
        "AI-assisted pre-transaction configuration checker for Indian merchants "
        "accepting international payments. Prototype only -- does not process "
        "real money and does not provide legal/tax advice."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(payment_configs.router)
app.include_router(compliance.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {
        "service": "Cross-Border Payment Compliance Guard API",
        "status": "ok",
        "demo_mode": {
            "razorpay": not settings.razorpay_configured,
            "ai": not settings.llm_configured,
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
