"""
API эндпоинты для OKX API
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.api.schemas import SignRequest, SignResponse, ErrorResponse
from app.services.okx_service import okx_service

router = APIRouter()


@router.get(
    "/sign",
    response_model=SignResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить подпись и временную метку",
    description="Генерирует OK-ACCESS-SIGN и OK-ACCESS-TIMESTAMP для запроса к OKX API"
)
async def get_signature(
    method: str = Query(..., description="HTTP метод (GET, POST, PUT, DELETE)"),
    path: str = Query(..., description="Путь API запроса"),
    body: str = Query("", description="Тело запроса (для POST/PUT запросов)")
):
    """
    Получить подпись и временную метку для OKX API
    
    - **method**: HTTP метод запроса
    - **path**: Путь API запроса
    - **body**: Тело запроса (опционально)
    
    Возвращает:
    - **ok_access_sign**: Подпись для заголовка OK-ACCESS-SIGN
    - **ok_access_timestamp**: Временная метка для заголовка OK-ACCESS-TIMESTAMP
    """
    try:
        logger.info(f"Запрос на генерацию подписи: {method} {path}")
        
        # Валидация входных данных
        if not method or not path:
            raise HTTPException(
                status_code=400, 
                detail="Метод и путь обязательны"
            )
        
        method = method.upper()
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise HTTPException(
                status_code=400, 
                detail="Неподдерживаемый HTTP метод"
            )
        
        # Получение подписи и временной метки
        result = okx_service.get_sign_and_timestamp(method, path, body)
        
        response = SignResponse(
            ok_access_sign=result['OK-ACCESS-SIGN'],
            ok_access_timestamp=result['OK-ACCESS-TIMESTAMP'],
            method=method,
            path=path
        )
        
        logger.info(f"Успешно сгенерирована подпись для {method} {path}")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка генерации подписи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sign",
    response_model=SignResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Получить подпись и временную метку (POST)",
    description="Генерирует OK-ACCESS-SIGN и OK-ACCESS-TIMESTAMP для запроса к OKX API"
)
async def get_signature_post(request: SignRequest):
    """
    Получить подпись и временную метку для OKX API (POST метод)
    
    Принимает JSON с параметрами:
    - **method**: HTTP метод запроса
    - **path**: Путь API запроса  
    - **body**: Тело запроса (опционально)
    
    Возвращает:
    - **ok_access_sign**: Подпись для заголовка OK-ACCESS-SIGN
    - **ok_access_timestamp**: Временная метка для заголовка OK-ACCESS-TIMESTAMP
    """
    try:
        logger.info(f"POST запрос на генерацию подписи: {request.method} {request.path}")
        
        # Валидация входных данных
        method = request.method.upper()
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise HTTPException(
                status_code=400, 
                detail="Неподдерживаемый HTTP метод"
            )
        
        # Получение подписи и временной метки
        result = okx_service.get_sign_and_timestamp(method, request.path, request.body)
        
        response = SignResponse(
            ok_access_sign=result['OK-ACCESS-SIGN'],
            ok_access_timestamp=result['OK-ACCESS-TIMESTAMP'],
            method=method,
            path=request.path
        )
        
        logger.info(f"Успешно сгенерирована подпись для {method} {request.path}")
        return response
        
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка генерации подписи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Проверка здоровья сервиса",
    description="Проверяет доступность OKX API и настройки приложения"
)
async def health_check():
    """
    Проверка здоровья сервиса
    
    Проверяет:
    - Доступность OKX API
    - Настройки приложения
    """
    try:
        # Проверяем доступность OKX API
        timestamp = okx_service.get_server_timestamp()
        
        return {
            "status": "healthy",
            "okx_api": "available",
            "server_timestamp": timestamp,
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