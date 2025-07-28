"""
Сервис для работы с OKX API
"""
import time
import hmac
import base64
import requests
from hashlib import sha256
from typing import Dict, Optional
from loguru import logger

from app.core.config import settings


class OKXService:
    """Сервис для работы с OKX API"""
    
    def __init__(self):
        self.base_url = settings.okx_base_url
        self.api_key = settings.okx_api_key
        self.api_secret = settings.okx_api_secret
        self.passphrase = settings.okx_passphrase
    
    def get_server_timestamp(self) -> str:
        """
        Получение текущей временной метки в формате ISO 8601 для OKX API
        
        Returns:
            str: Временная метка в формате ISO 8601 (например: 2025-07-25T12:30:45.123Z)
        """
        from datetime import datetime, timezone
        # Получаем UTC время без микросекунд
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        # Заменяем +00:00 на Z для соответствия требованиям OKX
        timestamp = timestamp.replace('+00:00', 'Z')
        logger.info(f"Сгенерирована временная метка ISO 8601 для OKX: {timestamp}")
        return timestamp
    
    def generate_signature(
        self, 
        timestamp: str, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> str:
        """
        Генерация подписи для OKX API
        
        Args:
            timestamp: Временная метка
            method: HTTP метод (GET, POST, etc.)
            request_path: Путь запроса
            body: Тело запроса (для POST запросов)
            
        Returns:
            str: Base64-кодированная подпись
        """
        try:
            message = f'{timestamp}{method.upper()}{request_path}{body}'
            
            if not self.api_secret:
                raise ValueError("API_SECRET не настроен")
            
            # Отладочная информация
            logger.info(f"Сообщение для подписи: '{message}'")
            logger.info(f"Длина сообщения: {len(message)}")
            logger.info(f"Body: '{body}' (длина: {len(body)})")
            
            mac = hmac.new(
                self.api_secret.encode('utf-8'), 
                message.encode('utf-8'), 
                sha256
            )
            signature = base64.b64encode(mac.digest()).decode()
            
            logger.info(f"Сгенерирована подпись: {signature}")
            return signature
            
        except Exception as e:
            logger.error(f"Ошибка генерации подписи: {e}")
            raise
    
    def get_auth_headers(
        self, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> Dict[str, str]:
        """
        Получение заголовков авторизации для OKX API
        
        Args:
            method: HTTP метод
            request_path: Путь запроса
            body: Тело запроса
            
        Returns:
            Dict[str, str]: Заголовки авторизации
        """
        try:
            timestamp = self.get_server_timestamp()
            signature = self.generate_signature(timestamp, method, request_path, body)
            
            headers = {
                'OK-ACCESS-KEY': self.api_key.strip(),
                'OK-ACCESS-SIGN': signature.strip(),  # Убираем лишние пробелы
                'OK-ACCESS-TIMESTAMP': timestamp.strip(),  # Убираем лишние пробелы
                'OK-ACCESS-PASSPHRASE': self.passphrase.strip(),
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Сгенерированы заголовки авторизации для {method} {request_path}")
            return headers
            
        except Exception as e:
            logger.error(f"Ошибка получения заголовков авторизации: {e}")
            raise
    
    def get_sign_and_timestamp(
        self, 
        method: str, 
        request_path: str, 
        body: str = ""
    ) -> Dict[str, str]:
        """
        Получение подписи и временной метки для запроса
        
        Args:
            method: HTTP метод
            request_path: Путь запроса
            body: Тело запроса
            
        Returns:
            Dict[str, str]: Словарь с подписью и временной меткой
        """
        try:
            timestamp = self.get_server_timestamp()
            signature = self.generate_signature(timestamp, method, request_path, body)
            
            result = {
                'OK-ACCESS-SIGN': signature.strip(),  # Убираем лишние пробелы
                'OK-ACCESS-TIMESTAMP': timestamp.strip()  # Убираем лишние пробелы
            }
            
            logger.info(f"Получены подпись и временная метка для {method} {request_path}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения подписи и временной метки: {e}")
            raise


    def place_market_order(self, side: str, notional: float) -> Dict:
        """
        Размещение рыночного ордера
        
        Args:
            side: Сторона (buy/sell)
            notional: Размер в USDT для покупки или BTC для продажи
            
        Returns:
            Dict: Результат размещения ордера
        """
        import json
        
        path = '/api/v5/trade/order'
        url = self.base_url + path
        
        body = {
            "instId": "BTC-USDT",
            "tdMode": "cash",
            "side": side,
            "ordType": "market",
            "ccy": "USDT" if side == "buy" else "BTC",
            "sz": str(notional)
        }
        
        body_str = json.dumps(body, separators=(",", ":"))
        logger.info(f"{side.upper()} BODY: {body_str}")
        
        headers = self.get_auth_headers("POST", path, body_str)
        headers['x-simulated-trading'] = '1'  # Демо режим
        
        response = requests.post(url, headers=headers, data=body_str)
        logger.info(f"{side.upper()} ORDER RESULT: {response.text}")
        
        return response.json()
    
    def get_balance(self, ccy: str) -> float:
        """
        Получение баланса валюты
        
        Args:
            ccy: Код валюты (BTC, USDT, etc.)
            
        Returns:
            float: Доступный баланс
        """
        path = f'/api/v5/account/balance?ccy={ccy}'
        url = self.base_url + path
        
        headers = self.get_auth_headers("GET", path)
        headers['x-simulated-trading'] = '1'  # Демо режим
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        return float(data['data'][0]['details'][0]['availBal'])
    
    def execute_trade_strategy(self, wait_minutes: int = 5) -> Dict:
        """
        Выполнение торговой стратегии: покупка -> ожидание -> продажа
        
        Args:
            wait_minutes: Время ожидания в минутах
            
        Returns:
            Dict: Результат выполнения стратегии
        """
        import time
        
        try:
            logger.info(f"=== НАЧАЛО ТОРГОВОЙ СТРАТЕГИИ ===")
            logger.info(f"Время ожидания: {wait_minutes} минут")
            
            # Шаг 1: Покупка на 100 USDT
            logger.info("Шаг 1: Покупка BTC на 100 USDT")
            buy_result = self.place_market_order("buy", notional=100)
            
            # Шаг 2: Ожидание
            logger.info(f"Шаг 2: Ожидание {wait_minutes} минут...")
            time.sleep(wait_minutes * 60)
            
            # Шаг 3: Продажа BTC
            logger.info("Шаг 3: Продажа BTC")
            btc_balance = self.get_balance("BTC")
            sell_result = self.place_market_order("sell", notional=btc_balance)
            
            result = {
                "strategy_completed": True,
                "wait_minutes": wait_minutes,
                "buy_order": buy_result,
                "sell_order": sell_result,
                "btc_balance_sold": btc_balance
            }
            
            logger.info(f"=== СТРАТЕГИЯ ЗАВЕРШЕНА ===")
            logger.info(f"Результат: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения торговой стратегии: {e}")
            raise


    def get_market_data(self, inst_id: str = "BTC-USDT") -> Dict:
        """
        Получение упрощенной рыночной информации
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Упрощенная рыночная информация
        """
        try:
            logger.info(f"Получение рыночных данных для {inst_id}")
            
            result = {}
            
            # 1. Только основные данные тикера
            ticker_path = f'/api/v5/market/ticker?instId={inst_id}'
            ticker_response = requests.get(self.base_url + ticker_path)
            ticker_data = ticker_response.json()
            
            # Извлекаем только нужные поля
            if 'data' in ticker_data and ticker_data['data']:
                ticker = ticker_data['data'][0]
                result['ticker'] = {
                    'instId': ticker.get('instId'),
                    'last': ticker.get('last'),
                    'lastSz': ticker.get('lastSz'),
                    'askPx': ticker.get('askPx'),
                    'askSz': ticker.get('askSz'),
                    'bidPx': ticker.get('bidPx'),
                    'bidSz': ticker.get('bidSz'),
                    'open24h': ticker.get('open24h'),
                    'high24h': ticker.get('high24h'),
                    'low24h': ticker.get('low24h'),
                    'volCcy24h': ticker.get('volCcy24h'),
                    'vol24h': ticker.get('vol24h'),
                    'sodUtc0': ticker.get('sodUtc0'),
                    'sodUtc8': ticker.get('sodUtc8'),
                    'ts': ticker.get('ts')
                }
            
            # 2. Упрощенный стакан ордеров (только первые 3 уровня)
            books_path = f'/api/v5/market/books?instId={inst_id}&sz=3'
            books_response = requests.get(self.base_url + books_path)
            books_data = books_response.json()
            
            if 'data' in books_data and books_data['data']:
                result['order_book'] = {
                    'instId': books_data['data'][0].get('instId'),
                    'bids': books_data['data'][0].get('bids', [])[:3],
                    'asks': books_data['data'][0].get('asks', [])[:3],
                    'ts': books_data['data'][0].get('ts')
                }
            
            # 3. Только последние 10 свечей (вместо 288)
            candles_path = f'/api/v5/market/candles?instId={inst_id}&bar=5m&limit=10'
            candles_response = requests.get(self.base_url + candles_path)
            candles_data = candles_response.json()
            
            if 'data' in candles_data:
                result['candles'] = candles_data['data'][:10]  # Только последние 10
            
            logger.info(f"Упрощенные рыночные данные для {inst_id} успешно получены")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения рыночных данных: {e}")
            raise
    
    def get_tickers_data(self, inst_type: str = "SPOT") -> Dict:
        """
        Получение данных по всем тикерам
        
        Args:
            inst_type: Тип инструмента (SPOT, SWAP, FUTURES, etc.)
            
        Returns:
            Dict: Данные всех тикеров
        """
        try:
            logger.info(f"Получение данных тикеров для {inst_type}")
            
            path = f'/api/v5/market/tickers?instType={inst_type}'
            response = requests.get(self.base_url + path)
            result = response.json()
            
            logger.info(f"Данные тикеров для {inst_type} успешно получены")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения данных тикеров: {e}")
            raise
    
    def get_currencies_data(self) -> Dict:
        """
        Получение информации о валютах
        
        Returns:
            Dict: Информация о валютах
        """
        try:
            logger.info("Получение информации о валютах")
            
            path = '/api/v5/public/currencies'
            response = requests.get(self.base_url + path)
            result = response.json()
            
            logger.info("Информация о валютах успешно получена")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о валютах: {e}")
            raise


# Глобальный экземпляр сервиса
okx_service = OKXService() 