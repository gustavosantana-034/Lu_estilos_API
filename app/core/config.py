from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Lu Estilo API"

    # Security settings
    SECRET_KEY: str = "your-secret-key-for-development-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/lu_estilo"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # WhatsApp API settings
    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v17.0"
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None

    # Twilio WhatsApp settings — declare explicitly!
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None

    # Sentry settings for error monitoring
    SENTRY_DSN: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # para ignorar variáveis extras (ou "allow" se preferir aceitar)
    }

settings = Settings()
