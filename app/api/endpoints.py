"""
API эндпоинты для OKX API
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from typing import Optional

from app.api.schemas import (
    SignRequest, SignResponse, ErrorResponse, 
    MarketDataRequest, MarketDataResponse, TickersRequest, CurrenciesResponse,
    BuyRequest, BuyResponse, SellRequest, SellResponse, BalanceResponse
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


@router.post(
    "/buy",
    response_model=BuyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Покупка BTC",
    description="Покупает BTC на указанную сумму USDT"
)
async def buy_btc(request: BuyRequest):
    """
    Покупка BTC на указанную сумму USDT
    
    Принимает JSON с параметрами:
    - **buy_amount**: Сумма в USDT для покупки BTC (по умолчанию 10.0)
    - **inst_id**: Инструмент для покупки (по умолчанию BTC-USDT)
    
    Выполняет:
    1. Покупка BTC на указанную сумму USDT
    2. Возвращает информацию о приобретенном BTC
    
    Возвращает:
    - **success**: Статус выполнения покупки
    - **buy_amount**: Сумма, потраченная на покупку
    - **buy_order**: Результат покупки
    - **btc_acquired**: Количество приобретенного BTC
    - **message**: Сообщение о результате операции
    """
    try:
        logger.info(f"Запрос на покупку BTC: сумма {request.buy_amount} USDT, инструмент {request.inst_id}")
        
        # Выполнение покупки BTC
        result = okx_service.buy_btc(buy_amount=request.buy_amount, inst_id=request.inst_id)
        
        response = BuyResponse(
            success=result["success"],
            buy_amount=result["buy_amount"],
            buy_order=result["buy_order"],
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
    "/buy",
    response_model=BuyResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Покупка BTC (GET)",
    description="Покупает BTC с параметрами из query string"
)
async def buy_btc_get(
    buy_amount: float = Query(default=10.0, description="Сумма в USDT для покупки BTC", gt=0),
    inst_id: str = Query(default="BTC-USDT", description="Инструмент для покупки")
):
    """
    Покупка BTC на указанную сумму USDT (GET метод)
    
    Параметры:
    - **buy_amount**: Сумма в USDT для покупки BTC (по умолчанию 10.0)
    - **inst_id**: Инструмент для покупки (по умолчанию BTC-USDT)
    
    Выполняет ту же операцию, что и POST /buy
    """
    try:
        logger.info(f"GET запрос на покупку BTC: сумма {buy_amount} USDT, инструмент {inst_id}")
        
        # Выполнение покупки BTC
        result = okx_service.buy_btc(buy_amount=buy_amount, inst_id=inst_id)
        
        response = BuyResponse(
            success=result["success"],
            buy_amount=result["buy_amount"],
            buy_order=result["buy_order"],
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


@router.post(
    "/sell",
    response_model=SellResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Продажа BTC",
    description="Продает BTC за USDT"
)
async def sell_btc(request: SellRequest):
    """
    Продажа BTC за USDT
    
    Принимает JSON с параметрами:
    - **sell_all**: Продать весь доступный BTC (по умолчанию True)
    - **sell_amount**: Количество BTC для продажи (если sell_all=False)
    - **inst_id**: Инструмент для продажи (по умолчанию BTC-USDT)
    
    Выполняет:
    1. Проверка доступного баланса BTC
    2. Продажа BTC (весь или указанное количество)
    3. Возвращает информацию о полученных USDT
    
    Возвращает:
    - **success**: Статус выполнения продажи
    - **sell_order**: Результат продажи
    - **btc_sold**: Количество проданного BTC
    - **usdt_received**: Количество полученных USDT
    - **message**: Сообщение о результате операции
    """
    try:
        logger.info(f"Запрос на продажу BTC: продать все {request.sell_all}, инструмент {request.inst_id}")
        if not request.sell_all:
            logger.info(f"Количество для продажи: {request.sell_amount} BTC")
        
        # Выполнение продажи BTC
        result = okx_service.sell_btc(
            sell_all=request.sell_all, 
            sell_amount=request.sell_amount, 
            inst_id=request.inst_id
        )
        
        response = SellResponse(
            success=result["success"],
            sell_order=result["sell_order"],
            btc_sold=result["btc_sold"],
            usdt_received=result["usdt_received"],
            message=result["message"]
        )
        
        logger.info(f"Продажа BTC завершена: {result['message']}")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка продажи BTC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sell",
    response_model=SellResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Продажа BTC (GET)",
    description="Продает BTC с параметрами из query string"
)
async def sell_btc_get(
    sell_all: bool = Query(default=True, description="Продать весь доступный BTC"),
    sell_amount: Optional[float] = Query(default=None, description="Количество BTC для продажи (если sell_all=False)", gt=0),
    inst_id: str = Query(default="BTC-USDT", description="Инструмент для продажи")
):
    """
    Продажа BTC за USDT (GET метод)
    
    Параметры:
    - **sell_all**: Продать весь доступный BTC (по умолчанию True)
    - **sell_amount**: Количество BTC для продажи (если sell_all=False)
    - **inst_id**: Инструмент для продажи (по умолчанию BTC-USDT)
    
    Выполняет ту же операцию, что и POST /sell
    """
    try:
        logger.info(f"GET запрос на продажу BTC: продать все {sell_all}, инструмент {inst_id}")
        if not sell_all:
            logger.info(f"Количество для продажи: {sell_amount} BTC")
        
        # Выполнение продажи BTC
        result = okx_service.sell_btc(
            sell_all=sell_all, 
            sell_amount=sell_amount, 
            inst_id=inst_id
        )
        
        response = SellResponse(
            success=result["success"],
            sell_order=result["sell_order"],
            btc_sold=result["btc_sold"],
            usdt_received=result["usdt_received"],
            message=result["message"]
        )
        
        logger.info(f"Продажа BTC завершена: {result['message']}")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка продажи BTC: {e}")
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


 