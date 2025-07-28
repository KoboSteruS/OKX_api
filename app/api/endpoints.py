"""
API эндпоинты для OKX API
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.api.schemas import (
    SignRequest, SignResponse, ErrorResponse, 
    TradeRequest, TradeResponse, MarketDataRequest, 
    MarketDataResponse, TickersRequest, CurrenciesResponse
)
from app.services.okx_service import okx_service

router = APIRouter()


@router.post(
    "/trade",
    response_model=TradeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Выполнить торговую стратегию",
    description="Выполняет торговую стратегию: покупка BTC на указанную сумму USDT -> ожидание -> продажа всего BTC"
)
async def execute_trade_strategy(request: TradeRequest):
    """
    Выполнение торговой стратегии
    
    Принимает JSON с параметрами:
    - **wait_minutes**: Время ожидания в минутах (по умолчанию 5)
    - **buy_amount**: Сумма в USDT для покупки BTC (по умолчанию 10.0)
    
    Выполняет:
    1. Покупка BTC на указанную сумму USDT
    2. Ожидание указанное количество минут
    3. Продажа всего доступного BTC
    
    Возвращает:
    - **strategy_completed**: Статус выполнения
    - **wait_minutes**: Время ожидания
    - **buy_amount**: Сумма, потраченная на покупку
    - **buy_order**: Результат покупки
    - **sell_order**: Результат продажи
    - **btc_balance_sold**: Количество проданного BTC
    """
    try:
        logger.info(f"Запрос на выполнение торговой стратегии: ожидание {request.wait_minutes} минут, сумма покупки {request.buy_amount} USDT")
        
        # Выполнение торговой стратегии
        result = okx_service.execute_trade_strategy(wait_minutes=request.wait_minutes, buy_amount=request.buy_amount)
        
        response = TradeResponse(
            strategy_completed=result["strategy_completed"],
            wait_minutes=result["wait_minutes"],
            buy_amount=result["buy_amount"],
            buy_order=result["buy_order"],
            sell_order=result["sell_order"],
            btc_balance_sold=result["btc_balance_sold"]
        )
        
        logger.info(f"Торговая стратегия успешно выполнена")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка выполнения торговой стратегии: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/trade",
    response_model=TradeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Выполнить торговую стратегию (GET)",
    description="Выполняет торговую стратегию с параметрами из query string"
)
async def execute_trade_strategy_get(
    wait_minutes: int = Query(default=5, description="Время ожидания в минутах", ge=1, le=60),
    buy_amount: float = Query(default=10.0, description="Сумма в USDT для покупки BTC", gt=0)
):
    """
    Выполнение торговой стратегии (GET метод)
    
    Параметры:
    - **wait_minutes**: Время ожидания в минутах (по умолчанию 5)
    - **buy_amount**: Сумма в USDT для покупки BTC (по умолчанию 10.0)
    
    Выполняет ту же стратегию, что и POST /trade
    """
    try:
        logger.info(f"GET запрос на выполнение торговой стратегии: ожидание {wait_minutes} минут, сумма покупки {buy_amount} USDT")
        
        # Выполнение торговой стратегии
        result = okx_service.execute_trade_strategy(wait_minutes=wait_minutes, buy_amount=buy_amount)
        
        response = TradeResponse(
            strategy_completed=result["strategy_completed"],
            wait_minutes=result["wait_minutes"],
            buy_amount=result["buy_amount"],
            buy_order=result["buy_order"],
            sell_order=result["sell_order"],
            btc_balance_sold=result["btc_balance_sold"]
        )
        
        logger.info(f"Торговая стратегия успешно выполнена")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка выполнения торговой стратегии: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.post(
    "/market-data",
    response_model=MarketDataResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить упрощенные рыночные данные",
    description="Получает основные рыночные данные: тикер, стакан (3 уровня), последние 10 свечей"
)
async def get_market_data(request: MarketDataRequest):
    """
    Получение комплексных рыночных данных
    
    Принимает JSON с параметрами:
    - **inst_id**: Инструмент (по умолчанию BTC-USDT)
    
    Возвращает:
    - **ticker**: Данные тикера (bid, ask, volume, etc.)
    - **order_book**: Стакан ордеров (глубина 5)
    - **candles**: Свечи за 24 часа (5-минутные интервалы, 288 свечей)
    - **instrument_info**: Информация об инструменте
    - **system_status**: Статус системы
    """
    try:
        logger.info(f"Запрос на получение рыночных данных для {request.inst_id}")
        
        # Получение рыночных данных
        result = okx_service.get_market_data(inst_id=request.inst_id)
        
        response = MarketDataResponse(
            inst_id=request.inst_id,
            ticker=result['ticker'],
            order_book=result['order_book'],
            candles=result['candles']
        )
        
        logger.info(f"Рыночные данные для {request.inst_id} успешно получены")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения рыночных данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/market-data",
    response_model=MarketDataResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить упрощенные рыночные данные (GET)",
    description="Получает основные рыночные данные с параметрами из query string: тикер, стакан (3 уровня), последние 10 свечей"
)
async def get_market_data_get(
    inst_id: str = Query(default="BTC-USDT", description="Инструмент для получения данных")
):
    """
    Получение комплексных рыночных данных (GET метод)
    
    Параметры:
    - **inst_id**: Инструмент (по умолчанию BTC-USDT)
    
    Возвращает ту же информацию, что и POST /market-data
    """
    try:
        logger.info(f"GET запрос на получение рыночных данных для {inst_id}")
        
        # Получение рыночных данных
        result = okx_service.get_market_data(inst_id=inst_id)
        
        response = MarketDataResponse(
            inst_id=inst_id,
            ticker=result['ticker'],
            order_book=result['order_book'],
            candles=result['candles']
        )
        
        logger.info(f"Рыночные данные для {inst_id} успешно получены")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения рыночных данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tickers",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить данные всех тикеров",
    description="Получает данные по всем тикерам указанного типа"
)
async def get_tickers_data(request: TickersRequest):
    """
    Получение данных всех тикеров
    
    Принимает JSON с параметрами:
    - **inst_type**: Тип инструмента (SPOT, SWAP, FUTURES, etc.)
    
    Возвращает данные всех тикеров указанного типа
    """
    try:
        logger.info(f"Запрос на получение данных тикеров для {request.inst_type}")
        
        # Получение данных тикеров
        result = okx_service.get_tickers_data(inst_type=request.inst_type)
        
        logger.info(f"Данные тикеров для {request.inst_type} успешно получены")
        return result
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения данных тикеров: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tickers",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить данные всех тикеров (GET)",
    description="Получает данные по всем тикерам с параметрами из query string"
)
async def get_tickers_data_get(
    inst_type: str = Query(default="SPOT", description="Тип инструмента")
):
    """
    Получение данных всех тикеров (GET метод)
    
    Параметры:
    - **inst_type**: Тип инструмента (SPOT, SWAP, FUTURES, etc.)
    
    Возвращает данные всех тикеров указанного типа
    """
    try:
        logger.info(f"GET запрос на получение данных тикеров для {inst_type}")
        
        # Получение данных тикеров
        result = okx_service.get_tickers_data(inst_type=inst_type)
        
        logger.info(f"Данные тикеров для {inst_type} успешно получены")
        return result
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения данных тикеров: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/currencies",
    response_model=CurrenciesResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить информацию о валютах",
    description="Получает информацию о всех валютах и их свойствах"
)
async def get_currencies_data():
    """
    Получение информации о валютах
    
    Возвращает информацию о всех валютах, включая:
    - Коды валют
    - Названия
    - Минимальные комиссии
    - Другие свойства
    """
    try:
        logger.info("Запрос на получение информации о валютах")
        
        # Получение информации о валютах
        result = okx_service.get_currencies_data()
        
        response = CurrenciesResponse(currencies=result)
        
        logger.info("Информация о валютах успешно получена")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения информации о валютах: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


 