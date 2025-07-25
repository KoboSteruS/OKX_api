"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field
from typing import Optional


class SignRequest(BaseModel):
    """Схема запроса для генерации подписи"""
    
    method: str = Field(
        ..., 
        description="HTTP метод (GET, POST, PUT, DELETE)",
        example="POST"
    )
    path: str = Field(
        ..., 
        description="Путь API запроса",
        example="/api/v5/trade/order"
    )
    body: Optional[str] = Field(
        default="", 
        description="Тело запроса (для POST/PUT запросов)",
        example='{"instId":"BTC-USDT","tdMode":"cash","side":"buy","ordType":"limit","sz":"0.001"}'
    )


class SignResponse(BaseModel):
    """Схема ответа с подписью и временной меткой"""
    
    ok_access_sign: str = Field(
        ..., 
        description="Подпись для заголовка OK-ACCESS-SIGN",
        example="dGhpcyBpcyBhIHRlc3Qgc2lnbmF0dXJl"
    )
    ok_access_timestamp: str = Field(
        ..., 
        description="Временная метка для заголовка OK-ACCESS-TIMESTAMP",
        example="1703123456"
    )
    method: str = Field(
        ..., 
        description="HTTP метод, для которого была сгенерирована подпись",
        example="POST"
    )
    path: str = Field(
        ..., 
        description="Путь API, для которого была сгенерирована подпись",
        example="/api/v5/trade/order"
    )


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    
    error: str = Field(
        ..., 
        description="Описание ошибки",
        example="API_SECRET не настроен"
    )
    detail: Optional[str] = Field(
        default=None, 
        description="Детальная информация об ошибке",
        example="Проверьте настройки в .env файле"
    ) 