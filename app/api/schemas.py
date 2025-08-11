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