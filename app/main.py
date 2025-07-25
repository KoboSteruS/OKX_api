"""
Основное FastAPI приложение для OKX API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from app.core.config import settings
from app.core.logger import setup_logger
from app.api.endpoints import router


# Инициализация логгера
setup_logger()

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API для генерации подписей и временных меток для OKX API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware для логирования запросов"""
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"Входящий запрос: {request.method} {request.url}")
    
    # Обрабатываем запрос
    response = await call_next(request)
    
    # Вычисляем время выполнения
    process_time = time.time() - start_time
    
    # Логируем результат
    logger.info(f"Запрос обработан: {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
    
    # Добавляем время выполнения в заголовки
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger.error(f"Необработанное исключение: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера",
            "detail": str(exc) if settings.debug else "Произошла неожиданная ошибка"
        }
    )


# Подключение роутеров
app.include_router(router, prefix="/api/v1", tags=["OKX API"])


@app.get("/", summary="Главная страница")
async def root():
    """
    Главная страница API
    
    Содержит информацию о доступных эндпоинтах
    """
    return {
        "message": "OKX API Helper",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
        "sign": "/api/v1/sign"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Запуск приложения {settings.app_name} v{settings.app_version}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 