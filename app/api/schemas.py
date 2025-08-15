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


class CancelOrderRequest(BaseModel):
    instId: str = Field(..., example="BTC-USDT")
    ordId: str = Field(..., example="1234567890")

class CancelOrderResponse(BaseModel):
    success: bool
    message: str
    cancelled_order: dict

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Ордер успешно отменён",
                "cancelled_order": {
                    "instId": "BTC-USDT",
                    "ordId": "1234567890",
                    "sCode": "0",
                    "sMsg": ""
                }
            }
        }



class FillsResponse(BaseModel):
    success: bool
    fills: list[dict]
    message: str

class ErrorResponse(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Ошибка отмены ордера: invalid order ID"
            }
        }


class SellRequest(BaseModel):
    sell_amount: float = Field(default=0.001, description="Количество BTC для продажи")
    inst_id: str = Field(default="BTC-USDT", description="Инструмент для торговли")

class SellResponse(BaseModel):
    success: bool
    sell_amount: float
    sell_order: dict
    message: str




class OrderItem(BaseModel):
    instId: str
    ordId: str
    px: str
    sz: str
    side: str
    ordType: str
    state: str
    cTime: Optional[str] = None
    uTime: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "instId": "BTC-USDT",
                "ordId": "1234567890",
                "px": "30000",
                "sz": "0.1",
                "side": "buy",
                "ordType": "limit",
                "state": "live",
                "cTime": "2025-08-04T08:01:23.456Z",
                "uTime": "2025-08-04T08:05:00.123Z"
            }
        }

class OrdersResponse(BaseModel):
    success: bool
    message: str
    orders: list[OrderItem]

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Ордера успешно получены",
                "orders": [
                    {
                        "instId": "BTC-USDT",
                        "ordId": "1234567890",
                        "px": "30000",
                        "sz": "0.1",
                        "side": "buy",
                        "ordType": "limit",
                        "state": "live",
                        "cTime": "2025-08-04T08:01:23.456Z",
                        "uTime": "2025-08-04T08:05:00.123Z"
                    },
                    {
                        "instId": "ETH-USDT",
                        "ordId": "987654321",
                        "px": "3500",
                        "sz": "0.5",
                        "side": "sell",
                        "ordType": "limit",
                        "state": "live",
                        "cTime": "2025-08-04T07:59:12.789Z",
                        "uTime": "2025-08-04T08:03:00.000Z"
                    }
                ]
            }
        }

class ErrorResponse(BaseModel):
    detail: str


# Схемы для торговых операций
class BuyRequest(BaseModel):
    """Схема запроса для покупки BTC с точками выхода"""
    
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
    take_profit_percent: float = Field(
        default=5.0,
        description="Процент для Take Profit (верхняя точка выхода)",
        example=5.0,
        gt=0
    )
    stop_loss_percent: float = Field(
        default=2.0,
        description="Процент для Stop Loss (нижняя точка выхода)",
        example=2.0,
        gt=0
    )


class BuyResponse(BaseModel):
    """Схема ответа операции покупки с точками выхода"""
    
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
    current_price: float = Field(
        ...,
        description="Текущая цена BTC на момент покупки",
        example=50000.0
    )
    take_profit_price: float = Field(
        ...,
        description="Цена Take Profit",
        example=52500.0
    )
    stop_loss_price: float = Field(
        ...,
        description="Цена Stop Loss",
        example=49000.0
    )
    buy_order: dict = Field(
        ...,
        description="Результат покупки BTC",
        example={"code": "0", "data": [{"ordId": "123456789"}]}
    )
    take_profit_order: dict = Field(
        ...,
        description="Take Profit ордер",
        example={"code": "0", "data": [{"ordId": "123456790"}]}
    )
    stop_loss_order: dict = Field(
        ...,
        description="Stop Loss ордер",
        example={"code": "0", "data": [{"ordId": "123456791"}]}
    )
    btc_acquired: float = Field(
        ...,
        description="Количество BTC, которое было куплено",
        example=0.001234
    )
    message: str = Field(
        ...,
        description="Сообщение о результате операции",
        example="BTC успешно куплен на 10.0 USDT по текущей цене 50000.0 с TP 52500.0 и SL 49000.0"
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
    """Схема ответа аналитического эндпоинта для BTC с множественными таймфреймами"""
    
    success: bool = Field(
        ...,
        description="Статус выполнения",
        example=True
    )
    inst_id: str = Field(
        ...,
        description="Инструмент (всегда BTC-USDT)",
        example="BTC-USDT"
    )
    market_data: dict = Field(
        ...,
        description="Рыночные данные: стакан ордеров и свечи по всем таймфреймам (1m:120, 5m:144, 15m:96, 1H:72, 4H:90, 1D:90)",
        example={
            "orderbook": [
                {
                    "asks": [["115000", "1.5"], ["115100", "2.0"]],
                    "bids": [["114900", "1.0"], ["114800", "1.5"]]
                }
            ],
            "candles": {
                "1m": [["1729123200000", "115000", "115200", "114800", "115100", "1.5", "172350", "0", "1"]],
                "5m": [["1729123200000", "115000", "115500", "114500", "115300", "7.2", "831600", "0", "1"]],
                "15m": [["1729123200000", "115000", "116000", "114000", "115800", "15.8", "1829400", "0", "1"]],
                "1H": [["1729123200000", "115000", "117000", "113000", "116500", "45.6", "5245800", "0", "1"]],
                "4H": [["1729123200000", "115000", "120000", "110000", "118000", "180.4", "20587200", "0", "1"]],
                "1D": [["1729123200000", "115000", "125000", "105000", "120000", "720.8", "87654300", "0", "1"]]
            }
        }
    )
    user_data: dict = Field(
        ...,
        description="Пользовательские данные (активные ордера, балансы)",
        example={
            "active_orders": [],
            "balances": {
                "USDT": {"available": "1000.0", "frozen": "0.0"},
                "BTC": {"available": "0.01", "frozen": "0.0"}
            }
        }
    )
    indicators: dict = Field(
        ...,
        description="Рыночные индикаторы BTC (цена, объем, изменения за 24ч)",
        example={
            "current_price": "115000",
            "volume_24h": "8057.66",
            "change_24h": "-2.58",
            "high_24h": "118887.4",
            "low_24h": "114116.5"
        }
    )
    timestamp: str = Field(
        ...,
        description="Временная метка запроса",
        example="2025-08-01T12:00:00Z"
    )
    message: str = Field(
        ...,
        description="Сообщение о результате",
        example="Аналитические данные по BTC успешно получены для всех таймфреймов"
    )


class MonitorResponse(BaseModel):
    """Схема ответа эндпоинта быстрого мониторинга BTC (1m свечи + основная аналитика)"""
    
    success: bool = Field(
        ...,
        description="Статус выполнения",
        example=True
    )
    inst_id: str = Field(
        ...,
        description="Инструмент (всегда BTC-USDT)",
        example="BTC-USDT"
    )
    candles_1m: list = Field(
        ...,
        description="Последние 10 свечей 1m для быстрого мониторинга",
        example=[
            ["1729123200000", "115000", "115200", "114800", "115100", "1.5", "172350", "0", "1"],
            ["1729123140000", "114950", "115000", "114900", "115000", "1.2", "137880", "0", "1"]
        ]
    )
    orderbook: list = Field(
        ...,
        description="Стакан ордеров BTC",
        example=[
            {
                "asks": [["115000", "1.5"], ["115100", "2.0"]],
                "bids": [["114900", "1.0"], ["114800", "1.5"]]
            }
        ]
    )
    active_orders: list = Field(
        ...,
        description="Активные ордера пользователя",
        example=[]
    )
    balances: dict = Field(
        ...,
        description="Балансы пользователя",
        example={
            "USDT": {"available": "1000.0", "frozen": "0.0"},
            "BTC": {"available": "0.01", "frozen": "0.0"}
        }
    )
    indicators: dict = Field(
        ...,
        description="Основные индикаторы BTC",
        example={
            "current_price": "115000",
            "volume_24h": "8057.66",
            "change_24h": "-2.58",
            "high_24h": "118887.4",
            "low_24h": "114116.5"
        }
    )
    timestamp: str = Field(
        ...,
        description="Временная метка запроса",
        example="2025-08-01T12:00:00Z"
    )
    message: str = Field(
        ...,
        description="Сообщение о результате",
        example="Мониторинговые данные по BTC успешно получены"
    ) 