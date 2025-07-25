"""
Настройка логирования для приложения
"""
from loguru import logger
import sys


def setup_logger():
    """Настройка логгера"""
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Добавляем обработчик для консоли
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Добавляем обработчик для файла
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        compression="zip"
    )


# Инициализация логгера
setup_logger() 