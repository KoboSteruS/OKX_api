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


# Новые схемы для разделенных операций покупки и продажи
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


# Новые схемы для аналитического API
class OrderBookEntry(BaseModel):
    """Схема записи стакана ордеров"""
    
    price: str = Field(
        ...,
        description="Цена",
        example="50000.0"
    )
    size: str = Field(
        ...,
        description="Размер",
        example="1.5"
    )
    num_orders: str = Field(
        ...,
        description="Количество ордеров",
        example="10"
    )


class CandleData(BaseModel):
    """Схема данных свечи"""
    
    timestamp: str = Field(
        ...,
        description="Временная метка",
        example="1703123456000"
    )
    open: str = Field(
        ...,
        description="Цена открытия",
        example="50000.0"
    )
    high: str = Field(
        ...,
        description="Максимальная цена",
        example="50100.0"
    )
    low: str = Field(
        ...,
        description="Минимальная цена",
        example="49900.0"
    )
    close: str = Field(
        ...,
        description="Цена закрытия",
        example="50050.0"
    )
    volume: str = Field(
        ...,
        description="Объем",
        example="100.5"
    )


class MarketData(BaseModel):
    """Схема рыночных данных"""
    
    orderbook: dict = Field(
        ...,
        description="Стакан ордеров",
        example={
            "bids": [{"price": "50000.0", "size": "1.5", "num_orders": "10"}],
            "asks": [{"price": "50001.0", "size": "1.0", "num_orders": "5"}]
        }
    )
    current_candles: list = Field(
        ...,
        description="Текущие свечи (последние 100)",
        example=[{"timestamp": "1703123456000", "open": "50000.0", "high": "50100.0", "low": "49900.0", "close": "50050.0", "volume": "100.5"}]
    )
    history_candles: list = Field(
        ...,
        description="Исторические свечи (последние 1000)",
        example=[{"timestamp": "1703123456000", "open": "50000.0", "high": "50100.0", "low": "49900.0", "close": "50050.0", "volume": "100.5"}]
    )


class UserOrder(BaseModel):
    """Схема пользовательского ордера"""
    
    ord_id: str = Field(
        ...,
        description="ID ордера",
        example="123456789"
    )
    inst_id: str = Field(
        ...,
        description="Инструмент",
        example="BTC-USDT"
    )
    side: str = Field(
        ...,
        description="Сторона (buy/sell)",
        example="buy"
    )
    ord_type: str = Field(
        ...,
        description="Тип ордера (market/limit)",
        example="limit"
    )
    px: str = Field(
        ...,
        description="Цена",
        example="50000.0"
    )
    sz: str = Field(
        ...,
        description="Размер",
        example="0.001"
    )
    state: str = Field(
        ...,
        description="Состояние ордера",
        example="live"
    )


class UserData(BaseModel):
    """Схема пользовательских данных"""
    
    active_orders: list = Field(
        ...,
        description="Активные ордера",
        example=[{"ord_id": "123456789", "inst_id": "BTC-USDT", "side": "buy", "ord_type": "limit", "px": "50000.0", "sz": "0.001", "state": "live"}]
    )
    balances: dict = Field(
        ...,
        description="Балансы",
        example={"BTC": 0.001234, "USDT": 100.5}
    )


class MarketIndicators(BaseModel):
    """Схема рыночных индикаторов"""
    
    current_price: str = Field(
        ...,
        description="Текущая цена",
        example="50000.0"
    )
    volume_24h: str = Field(
        ...,
        description="Объем за 24 часа",
        example="1000000.0"
    )
    change_24h: str = Field(
        ...,
        description="Изменение за 24 часа",
        example="2.5"
    )
    high_24h: str = Field(
        ...,
        description="Максимум за 24 часа",
        example="51000.0"
    )
    low_24h: str = Field(
        ...,
        description="Минимум за 24 часа",
        example="49000.0"
    )


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