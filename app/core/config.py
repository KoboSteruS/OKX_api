"""
Конфигурация приложения для OKX API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Настройки FastAPI
    app_name: str = "OKX API Helper"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Настройки OKX API
    okx_base_url: str = "https://www.okx.com"  # Основной URL для демо-режима
    okx_api_key: Optional[str] = None
    okx_api_secret: Optional[str] = None
    okx_passphrase: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings() 