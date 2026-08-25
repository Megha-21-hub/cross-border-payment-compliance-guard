"""
Central configuration for the app. All secrets/config come from environment
variables (loaded from .env in local dev). NOTHING is hard-coded here.

If RAZORPAY_KEY_ID/SECRET or LLM_API_KEY are missing, the app runs in
DEMO MODE automatically -- this is a deliberate product requirement so the
prototype can always be demoed, e.g. at the hackathon, even with no
credentials configured.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./compliance_guard.db"

    jwt_secret_key: str = "insecure-dev-secret-change-me"
    jwt_expire_minutes: int = 120
    jwt_algorithm: str = "HS256"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    frontend_origin: str = "http://localhost:5173"

    @property
    def razorpay_configured(self) -> bool:
        return bool(self.razorpay_key_id and self.razorpay_key_secret)

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key)


settings = Settings()
