from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Smart Home API"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FACE_VERIFICATION_TTL_SECONDS: int = 60
    FACE_MIN_CONFIDENCE: float = 0.8
    FACE_AUTHORIZED_PERSON_IDS: List[str] = []

    # Camera Settings
    CAMERA_FPS: int = 30
    CAMERA_RESOLUTION: str = "1920x1080"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
