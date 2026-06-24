"""
User Management Service - Configuration Settings

This module provides environment-based configuration for the User Management Service.
Follows 12-factor app principles with environment variables.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    User Management Service Configuration
    """
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Service Info
    SERVICE_NAME: str = "GDB-User-Service"
    TITLE: str = "GDB User Management Service"
    DESCRIPTION: str = "FastAPI service for user management with role-based access control"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # Database Settings (gdb_users_db)
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "gdb_users_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    
    # Security Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # JWT Settings (SHARED)
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Inter-Service URLs (StandardizedPlural and LegacySingular)
    ACCOUNTS_SERVICE_URL: str = "http://localhost:8001"
    ACCOUNT_SERVICE_URL: str = "http://localhost:8001"
    
    TRANSACTIONS_SERVICE_URL: str = "http://localhost:8002"
    TRANSACTION_SERVICE_URL: str = "http://localhost:8002"
    
    USERS_SERVICE_URL: str = "http://localhost:8003"
    USER_SERVICE_URL: str = "http://localhost:8003"
    
    AUTH_SERVICE_URL: str = "http://localhost:8004"
    AADHAR_SERVICE_URL: str = "http://localhost:8005"
    COMPANY_SERVICE_URL: str = "http://localhost:8006"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8007"
    PAYMENT_GATEWAY_SERVICE_URL: str = "http://localhost:8008"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/users_service.log"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # API prefix
    API_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


# Load settings from environment
settings = Settings()

# Schema configuration for multi-tenant database
SCHEMA_NAME = "users_service"

# Update search_path for PostgreSQL
async def set_schema_search_path(connection):
    """Set the search path to use the correct schema."""
    await connection.execute(f"SET search_path TO users_service, public")
