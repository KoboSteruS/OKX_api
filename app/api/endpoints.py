"""
API эндпоинты для OKX API
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from typing import Optional

from app.api.schemas import (
    ErrorResponse, BuyRequest, BuyResponse, BalanceResponse, AnalyticsResponse, OrdersResponse, CancelOrderRequest, CancelOrderResponse,FillsResponse
)
from app.services.okx_service import okx_service

router = APIRouter()


@router.get(
    "/health",
    summary="Проверка здоровья сервиса",
    description="Проверяет настройки приложения"
)
async def health_check():
    """
    Проверка здоровья сервиса
    
    Проверяет:
    - Настройки приложения
    - Генерацию временной метки
    """
    try:
        # Генерируем локальную временную метку
        timestamp = okx_service.get_server_timestamp()
        
        return {
            "status": "healthy",
            "timestamp": timestamp,
            "api_key_configured": bool(okx_service.api_key),
            "api_secret_configured": bool(okx_service.api_secret),
            "passphrase_configured": bool(okx_service.passphrase)
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Сервис недоступен: {str(e)}"
        )


@router.get(
    "/test-connection",
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Тестирование соединения с OKX API",
    description="Проверяет соединение с OKX API и диагностирует проблемы"
)
async def test_connection():
    """
    Тестирование соединения с OKX API
    
    Проверяет:
    - Доступность OKX API
    - SSL/TLS соединение
    - Сетевые настройки
    
    Возвращает:
    - **status**: Статус соединения (success/ssl_error/network_error/unknown_error)
    - **message**: Описание результата
    - **suggestion**: Рекомендации по исправлению (если есть)
    """
    try:
        logger.info("Запрос на тестирование соединения с OKX API")
        
        # Тестирование соединения
        result = okx_service.test_connection()
        
        logger.info(f"Результат тестирования: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка тестирования соединения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/orders/cancel",
    response_model=CancelOrderResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Отменить ордер",
    description="Отменяет ордер по идентификатору и инструменту"
)
async def cancel_order(request: CancelOrderRequest):
    """
    Отмена ордера по instId и ordId

    Пример:
    - instId: BTC-USDT
    - ordId: 1234567890
    """
    try:
        logger.info(f"Запрос на отмену ордера: {request.ordId}")

        result = okx_service.cancel_order(
            inst_id=request.instId,
            ord_id=request.ordId
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])

        return CancelOrderResponse(
            success=True,
            message=result["message"],
            cancelled_order=result["cancelled_order"]
        )

    except Exception as e:
        logger.error(f"Ошибка отмены ордера: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.post(
    "/buy",
    response_model=BuyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Покупка BTC с точками выхода",
    description="Покупает BTC по текущей рыночной цене и устанавливает Take Profit и Stop Loss ордера"
)
async def buy_btc(request: BuyRequest):
    """
    Покупка BTC с точками выхода
    
    Принимает JSON с параметрами:
    - **buy_amount**: Сумма в USDT для покупки BTC (по умолчанию 10.0)
    - **inst_id**: Инструмент для покупки (по умолчанию BTC-USDT)
    - **take_profit_percent**: Процент для Take Profit (по умолчанию 5.0%)
    - **stop_loss_percent**: Процент для Stop Loss (по умолчанию 2.0%)
    
    Выполняет:
    1. Покупка BTC по текущей рыночной цене
    2. Установка Take Profit ордера (автоматическая продажа при росте)
    3. Установка Stop Loss ордера (автоматическая продажа при падении)
    
    Возвращает:
    - **success**: Статус выполнения покупки
    - **buy_amount**: Сумма, потраченная на покупку
    - **current_price**: Текущая цена BTC на момент покупки
    - **take_profit_price**: Цена Take Profit
    - **stop_loss_price**: Цена Stop Loss
    - **buy_order**: Результат покупки
    - **take_profit_order**: Take Profit ордер
    - **stop_loss_order**: Stop Loss ордер
    - **btc_acquired**: Количество приобретенного BTC
    - **message**: Сообщение о результате операции
    """
    try:
        logger.info(f"Запрос на покупку BTC: сумма {request.buy_amount} USDT, TP {request.take_profit_percent}%, SL {request.stop_loss_percent}%")
        
        # Выполнение покупки BTC с точками выхода
        result = okx_service.buy_btc_with_exits(
            buy_amount=request.buy_amount,
            inst_id=request.inst_id,
            take_profit_percent=request.take_profit_percent,
            stop_loss_percent=request.stop_loss_percent
        )
        
        response = BuyResponse(
            success=result["success"],
            buy_amount=result["buy_amount"],
            current_price=result["current_price"],
            take_profit_price=result["take_profit_price"],
            stop_loss_price=result["stop_loss_price"],
            buy_order=result["buy_order"],
            take_profit_order=result["take_profit_order"],
            stop_loss_order=result["stop_loss_order"],
            btc_acquired=result["btc_acquired"],
            message=result["message"]
        )
        
        logger.info(f"Покупка BTC завершена: {result['message']}")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка покупки BTC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/balance",
    response_model=BalanceResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Получить балансы",
    description="Получает балансы всех валют"
)
async def get_balances():
    """
    Получение балансов всех валют
    
    Возвращает:
    - **success**: Статус получения балансов
    - **balances**: Балансы по всем валютам
    - **message**: Сообщение о результате операции
    """
    try:
        logger.info("Запрос на получение балансов всех валют")
        
        # Получение балансов
        result = okx_service.get_balances()
        
        response = BalanceResponse(
            success=result["success"],
            balances=result["balances"],
            message=result["message"]
        )
        
        logger.info(f"Балансы получены: {result['message']}")
        return response
        
    except Exception as e:
        logger.error(f"Ошибка получения балансов: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get(
    "/orders",
    response_model=OrdersResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Получить все открытые ордера",
    description="Возвращает список всех открытых ордеров на OKX"
)
async def get_orders():
    """
    Получение открытых ордеров

    Возвращает:
    - **success**: Статус
    - **orders**: Список ордеров
    - **message**: Описание результата
    """
    try:
        logger.info("Запрос на получение открытых ордеров")

        result = okx_service.get_orders()

        response = OrdersResponse(
            success=result["success"],
            message=result["message"],
            orders=result["orders"]
        )

        return response

    except Exception as e:
        logger.error(f"Ошибка получения ордеров: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/market/analytics",
    response_model=AnalyticsResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить аналитические данные",
    description="Получает полные аналитические данные для n8n: стакан ордеров, свечи, активные ордера, балансы, индикаторы"
)


@router.get(
    "/fills",
    response_model=FillsResponse,
    responses={
        500: {"model": ErrorResponse}
    },
    summary="Получить последние сделки",
    description="Возвращает список последних заполненных ордеров (сделок) на OKX"
)
async def get_fills(
    inst_type: Optional[str] = Query(default=None, description="Тип инструмента (SPOT, MARGIN, SWAP, FUTURES, OPTION)"),
    inst_id: Optional[str] = Query(default=None, description="Инструмент (например, BTC-USDT)"),
    ord_id: Optional[str] = Query(default=None, description="ID ордера"),
    after: Optional[str] = Query(default=None, description="Курсор пагинации (ID сделки, после которой запрашиваются данные)"),
    before: Optional[str] = Query(default=None, description="Курсор пагинации (ID сделки, до которой запрашиваются данные)"),
    limit: int = Query(default=100, description="Количество записей (максимум 100)", ge=1, le=100)
):
    """
    Получение последних сделок (заполненных ордеров)
    
    Параметры:
    - **inst_type**: Тип инструмента (SPOT, MARGIN, SWAP, FUTURES, OPTION)
    - **inst_id**: Инструмент (например, BTC-USDT)
    - **ord_id**: ID ордера
    - **after**: Курсор пагинации (ID сделки, после которой запрашиваются данные)
    - **before**: Курсор пагинации (ID сделки, до которой запрашиваются данные)
    - **limit**: Количество записей (по умолчанию 100, максимум 100)
    
    Возвращает:
    - **success**: Статус
    - **fills**: Список сделок
    - **message**: Описание результата
    """
    try:
        logger.info(f"Запрос на получение последних сделок: inst_type={inst_type}, inst_id={inst_id}, ord_id={ord_id}, limit={limit}")
        
        result = okx_service.get_trade_fills(
            inst_type=inst_type,
            inst_id=inst_id,
            ord_id=ord_id,
            after=after,
            before=before,
            limit=limit
        )
        
        response = FillsResponse(
            success=result["success"],
            message=result["message"],
            fills=result["fills"]
        )
        
        logger.info(f"Сделки получены: {result['message']}")
        return response
        
    except Exception as e:
        logger.error(f"Ошибка получения сделок: {e}")
        raise HTTPException(status_code=500, detail=str(e))




async def get_market_analytics(
    inst_id: str = Query(default="BTC-USDT", description="Инструмент для анализа"),
    bar: str = Query(default="1m", description="Интервал свечей (1m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 12H, 1D, 1W, 1M, 3M, 6M, 1Y)"),
    depth: int = Query(default=20, description="Глубина стакана ордеров", ge=1, le=100),
    current_limit: int = Query(default=100, description="Количество текущих свечей", ge=1, le=1000),
    history_limit: int = Query(default=1000, description="Количество исторических свечей", ge=1, le=3000)
):
    """
    Получение полных аналитических данных для n8n
    
    Возвращает в одном запросе:
    - **Стакан ордеров** (order book) - для анализа ликвидности
    - **Текущие свечи** - для понимания текущей ситуации
    - **Исторические свечи** - для технического анализа
    - **Активные ордера** - текущие ордера пользователя
    - **Балансы** - доступные средства
    - **Рыночные индикаторы** - цена, объем, изменения
    
    Параметры:
    - **inst_id**: Инструмент для анализа (по умолчанию BTC-USDT)
    - **bar**: Интервал свечей (по умолчанию 1m)
    - **depth**: Глубина стакана ордеров (по умолчанию 20)
    - **current_limit**: Количество текущих свечей (по умолчанию 100)
    - **history_limit**: Количество исторических свечей (по умолчанию 1000)
    
    Использование в n8n:
    - Один запрос предоставляет всю необходимую информацию
    - Позволяет быстро принимать торговые решения
    - Эффективно для автоматизации торговых стратегий
    """
    try:
        logger.info(f"Запрос аналитических данных для {inst_id}")
        logger.info(f"Параметры: bar={bar}, depth={depth}, current_limit={current_limit}, history_limit={history_limit}")
        
        # Получение аналитических данных
        result = okx_service.get_market_analytics(
            inst_id=inst_id,
            bar=bar,
            depth=depth,
            current_limit=current_limit,
            history_limit=history_limit
        )
        
        # Создаем ответ с правильной структурой
        response = AnalyticsResponse(
            success=result["success"],
            inst_id=result["inst_id"],
            market_data=result["market_data"],
            user_data=result["user_data"],
            indicators=result["indicators"],
            timestamp=result["timestamp"],
            message=result["message"]
        )
        
        logger.info(f"Аналитические данные для {inst_id} успешно получены")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения аналитических данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


 