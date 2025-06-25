from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:2300@localhost:3306/max_queryhub"
    
    # Security
    JWT_SECRET_KEY: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # External APIs
    MAXPLATFORM_API_URL: str = "http://localhost:8000"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8006
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Scheduler
    AUTO_CLOSE_DAYS_DEFAULT: int = 90
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3006", "http://localhost:3000", "http://localhost:8000","http://localhost:8006"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
