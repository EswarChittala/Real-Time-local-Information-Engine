from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    project_name: str = "Real-Time Hyperlocal Information Engine"
    version: str = "0.1.0"
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./hyperlocal.db"
    
    # Traffic Freshness & Observation Config
    traffic_report_max_age_minutes: int = 30
    shop_report_max_age_minutes: int = 180
    default_report_max_age_minutes: int = 60
    
    # Verification & Consensus
    min_independent_witnesses_confirmed: int = 2
    
    # Twilio / WhatsApp (Optional initially)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None
    
    # AI / LLM Fallback (Optional)
    groq_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
