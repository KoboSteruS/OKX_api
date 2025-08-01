"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field
from typing import Optional


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


# Схемы для торговых операций
class BuyRequest(BaseModel):
    """Схема запроса для покупки BTC"""
    
    buy_amount: float = Field(
        default=10.0,
        description="Сумма в USDT для покупки BTC",
        example=10.0,
        gt=0
    )
    inst_id: str = Field(
        default="BTC-USDT",
        description="Инструмент для покупки",
        example="BTC-USDT"
    )


class BuyResponse(BaseModel):
    """Схема ответа операции покупки"""
    
    success: bool = Field(
        ...,
        description="Статус выполнения покупки",
        example=True
    )
    buy_amount: float = Field(
        ...,
        description="Сумма в USDT, потраченная на покупку BTC",
        example=10.0
    )
    buy_order: dict = Field(
        ...,
        description="Результат покупки BTC",
        example={"code": "0", "data": [{"ordId": "123456789"}]}
    )
    btc_acquired: float = Field(
        ...,
        description="Количество BTC, которое было куплено",
        example=0.001234
    )
    message: str = Field(
        ...,
        description="Сообщение о результате операции",
        example="BTC успешно куплен на 10.0 USDT"
    )


class SellRequest(BaseModel):
    """Схема запроса для продажи BTC"""
    
    sell_all: bool = Field(
        default=True,
        description="Продать весь доступный BTC",
        example=True
    )
    sell_amount: Optional[float] = Field(
        default=None,
        description="Количество BTC для продажи (если sell_all=False)",
        example=0.001,
        gt=0
    )
    inst_id: str = Field(
        default="BTC-USDT",
        description="Инструмент для продажи",
        example="BTC-USDT"
    )


class SellResponse(BaseModel):
    """Схема ответа операции продажи"""
    
    success: bool = Field(
        ...,
        description="Статус выполнения продажи",
        example=True
    )
    sell_order: dict = Field(
        ...,
        description="Результат продажи BTC",
        example={"code": "0", "data": [{"ordId": "987654321"}]}
    )
    btc_sold: float = Field(
        ...,
        description="Количество BTC, которое было продано",
        example=0.001234
    )
    usdt_received: float = Field(
        ...,
        description="Количество USDT, полученное за продажу",
        example=10.5
    )
    message: str = Field(
        ...,
        description="Сообщение о результате операции",
        example="BTC успешно продан за 10.5 USDT"
    )


class BalanceResponse(BaseModel):
    """Схема ответа с балансом"""
    
    success: bool = Field(
        ...,
        description="Статус получения баланса",
        example=True
    )
    balances: dict = Field(
        ...,
        description="Балансы по валютам",
        example={"BTC": 0.001234, "USDT": 100.5}
    )
    message: str = Field(
        ...,
        description="Сообщение о результате операции",
        example="Баланс успешно получен"
    )


# Схемы для аналитического API
class AnalyticsResponse(BaseModel):
    """Схема ответа аналитического эндпоинта"""
    
    success: bool = Field(
        ...,
        description="Статус выполнения",
        example=True
    )
    inst_id: str = Field(
        ...,
        description="Инструмент",
        example="BTC-USDT"
    )
    market_data: dict = Field(
        ...,
        description="Рыночные данные (стакан ордеров, свечи)"
    )
    user_data: dict = Field(
        ...,
        description="Пользовательские данные (активные ордера, балансы)"
    )
    indicators: dict = Field(
        ...,
        description="Рыночные индикаторы (цена, объем, изменения)"
    )
    timestamp: str = Field(
        ...,
        description="Временная метка запроса",
        example="2025-07-29T11:52:05Z"
    )
    message: str = Field(
        ...,
        description="Сообщение о результате",
        example="Аналитические данные успешно получены"
    ) 