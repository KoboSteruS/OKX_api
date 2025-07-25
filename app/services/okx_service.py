"""
Сервис для работы с OKX API
"""
import time
import hmac
import base64
import requests
from hashlib import sha256
from typing import Dict, Optional
from loguru import logger

from app.core.config import settings


class OKXService:
    """Сервис для работы с OKX API"""
    
    def __init__(self):
        self.base_url = settings.okx_base_url
        self.api_key = settings.okx_api_key
        self.api_secret = settings.okx_api_secret
        self.passphrase = settings.okx_passphrase
    
    def get_server_timestamp(self) -> str:
        """
        Получение текущей временной метки в формате ISO 8601
        
        Returns:
            str: Временная метка в формате ISO 8601 (например: 2025-07-25T12:30:45.123Z)
        """
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Сгенерирована временная метка ISO 8601: {timestamp}")
        return timestamp
    
    def generate_signature(
        self, 
        timestamp: str, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> str:
        """
        Генерация подписи для OKX API
        
        Args:
            timestamp: Временная метка
            method: HTTP метод (GET, POST, etc.)
            request_path: Путь запроса
            body: Тело запроса (для POST запросов)
            
        Returns:
            str: Base64-кодированная подпись
        """
        try:
            message = f'{timestamp}{method.upper()}{request_path}{body}'
            
            if not self.api_secret:
                raise ValueError("API_SECRET не настроен")
            
            mac = hmac.new(
                self.api_secret.encode('utf-8'), 
                message.encode('utf-8'), 
                sha256
            )
            signature = base64.b64encode(mac.digest()).decode()
            
            logger.debug(f"Сгенерирована подпись для: {method} {request_path}")
            return signature
            
        except Exception as e:
            logger.error(f"Ошибка генерации подписи: {e}")
            raise
    
    def get_auth_headers(
        self, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> Dict[str, str]:
        """
        Получение заголовков авторизации для OKX API
        
        Args:
            method: HTTP метод
            request_path: Путь запроса
            body: Тело запроса
            
        Returns:
            Dict[str, str]: Заголовки авторизации
        """
        try:
            timestamp = self.get_server_timestamp()
            signature = self.generate_signature(timestamp, method, request_path, body)
            
            headers = {
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Сгенерированы заголовки авторизации для {method} {request_path}")
            return headers
            
        except Exception as e:
            logger.error(f"Ошибка получения заголовков авторизации: {e}")
            raise
    
    def get_sign_and_timestamp(
        self, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> Dict[str, str]:
        """
        Получение подписи и временной метки для запроса
        
        Args:
            method: HTTP метод
            request_path: Путь запроса
            body: Тело запроса
            
        Returns:
            Dict[str, str]: Словарь с подписью и временной меткой
        """
        try:
            timestamp = self.get_server_timestamp()
            signature = self.generate_signature(timestamp, method, request_path, body)
            
            result = {
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp
            }
            
            logger.info(f"Получены подпись и временная метка для {method} {request_path}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения подписи и временной метки: {e}")
            raise


# Глобальный экземпляр сервиса
okx_service = OKXService() 