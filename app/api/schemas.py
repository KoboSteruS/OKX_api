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


class TradeRequest(BaseModel):
    """Схема запроса для торговой стратегии"""
    
    wait_minutes: int = Field(
        default=5,
        description="Время ожидания в минутах между покупкой и продажей",
        example=5,
        ge=1,
        le=60
    )
    buy_amount: float = Field(
        default=10.0,
        description="Сумма в USDT для покупки BTC",
        example=10.0,
        gt=0
    )


class TradeResponse(BaseModel):
    """Схема ответа торговой стратегии"""
    
    strategy_completed: bool = Field(
        ...,
        description="Статус выполнения стратегии",
        example=True
    )
    wait_minutes: int = Field(
        ...,
        description="Время ожидания в минутах",
        example=5
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
    sell_order: dict = Field(
        ...,
        description="Результат продажи BTC",
        example={"code": "0", "data": [{"ordId": "987654321"}]}
    )
    btc_balance_sold: float = Field(
        ...,
        description="Количество BTC, которое было продано",
        example=0.001234
    )


class MarketDataRequest(BaseModel):
    """Схема запроса для получения рыночных данных"""
    
    inst_id: str = Field(
        default="BTC-USDT",
        description="Инструмент для получения данных",
        example="BTC-USDT"
    )


class MarketDataResponse(BaseModel):
    """Схема ответа с упрощенными рыночными данными"""
    
    inst_id: str = Field(
        ...,
        description="Инструмент",
        example="BTC-USDT"
    )
    ticker: dict = Field(
        ...,
        description="Основные данные тикера",
        example={"instId": "BTC-USDT", "last": "50000", "askPx": "50001", "bidPx": "50000"}
    )
    order_book: dict = Field(
        ...,
        description="Стакан ордеров (3 уровня)",
        example={"instId": "BTC-USDT", "bids": [["50000", "1.0"]], "asks": [["50001", "1.0"]]}
    )
    candles: list = Field(
        ...,
        description="Последние 10 свечей (5-минутные интервалы)",
        example=[["1703123456", "50000", "50001", "50000", "50000", "100"]]
    )


class TickersRequest(BaseModel):
    """Схема запроса для получения данных тикеров"""
    
    inst_type: str = Field(
        default="SPOT",
        description="Тип инструмента (SPOT, SWAP, FUTURES, etc.)",
        example="SPOT"
    )


class CurrenciesResponse(BaseModel):
    """Схема ответа с информацией о валютах"""
    
    currencies: dict = Field(
        ...,
        description="Информация о валютах",
        example={"code": "0", "data": [{"ccy": "BTC", "name": "Bitcoin", "minFee": "0.0001"}]}
    ) 