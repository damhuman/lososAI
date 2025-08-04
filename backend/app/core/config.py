from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Seafood Store API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            path=values.data.get("POSTGRES_DB"),
        )
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None
    
    @field_validator("REDIS_URL", mode="before")
    def assemble_redis_url(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return f"redis://{values.data.get('REDIS_HOST')}:{values.data.get('REDIS_PORT')}"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    
    # Web App
    WEB_APP_URL: str
    
    # S3 Configuration
    S3_ENDPOINT_URL: str = "https://fra1.digitaloceanspaces.com"
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "losos"
    S3_REGION: str = "fra1"
    S3_PUBLIC_URL: str = "https://losos.fra1.digitaloceanspaces.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()