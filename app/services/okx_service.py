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
        
        # Настройка сессии requests для лучшей производительности
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OKX-Trading-Bot/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
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
    
    def test_connection(self) -> Dict:
        """
        Тестирование соединения с OKX API
        
        Returns:
            Dict: Результат тестирования
        """
        try:
            logger.info("Тестирование соединения с OKX API...")
            
            # Тест 1: Простой GET запрос к публичному API
            test_url = f"{self.base_url}/api/v5/public/time"
            
            try:
                response = self.session.get(
                    test_url,
                    timeout=10,
                    verify=True
                )
                if response.status_code == 200:
                    logger.info("✅ Соединение с OKX API успешно")
                    return {
                        "status": "success",
                        "message": "Соединение с OKX API работает",
                        "response": response.json()
                    }
                else:
                    logger.error(f"❌ Ошибка HTTP: {response.status_code}")
                    return {
                        "status": "error",
                        "message": f"HTTP ошибка: {response.status_code}",
                        "response": response.text
                    }
            except requests.exceptions.SSLError as e:
                logger.error(f"❌ SSL ошибка: {e}")
                return {
                    "status": "ssl_error",
                    "message": f"SSL ошибка: {e}",
                    "suggestion": "Проверьте настройки SSL сертификатов на сервере"
                }
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Ошибка сети: {e}")
                return {
                    "status": "network_error",
                    "message": f"Ошибка сети: {e}",
                    "suggestion": "Проверьте интернет соединение и файрвол"
                }
                
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
            return {
                "status": "unknown_error",
                "message": f"Неожиданная ошибка: {e}"
            }
    
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
                'OK-ACCESS-SIGN': signature.strip(),
                'OK-ACCESS-TIMESTAMP': timestamp.strip(),
                'OK-ACCESS-PASSPHRASE': self.passphrase.strip(),
                'Content-Type': 'application/json',
                'x-simulated-trading': '1'  # Демо режим
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


    def place_market_order(self, side: str, notional: float, inst_id: str = "BTC-USDT") -> Dict:
        """
        Размещение рыночного ордера
        
        Args:
            side: Сторона (buy/sell)
            notional: Размер в USDT для покупки или BTC для продажи
            inst_id: Инструмент для торговли (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Результат размещения ордера
        """
        import json
        
        path = '/api/v5/trade/order'
        url = self.base_url + path
        
        body = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": side,
            "ordType": "market",
            "ccy": "USDT" if side == "buy" else "BTC",
            "sz": str(notional)
        }
        
        body_str = json.dumps(body, separators=(",", ":"))
        logger.info(f"{side.upper()} BODY: {body_str}")
        
        headers = self.get_auth_headers("POST", path, body_str)
        
        try:
            response = self.session.post(
                url, 
                headers=headers, 
                data=body_str,
                timeout=30,
                verify=True
            )
            logger.info(f"{side.upper()} ORDER RESULT: {response.text}")
            return response.json()
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при размещении ордера: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при размещении ордера: {e}")
            raise
    
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
        
        try:
            response = self.session.get(
                url, 
                headers=headers,
                timeout=30,
                verify=True
            )
            data = response.json()
            
            # Проверяем наличие ошибки в ответе
            if 'code' in data and data['code'] != '0':
                logger.error(f"Ошибка API при получении баланса {ccy}: {data}")
                return 0.0
            
            # Проверяем структуру данных
            if 'data' not in data or not data['data']:
                logger.warning(f"Нет данных баланса для {ccy}")
                return 0.0
            
            # Извлекаем баланс
            for account in data['data']:
                if 'details' in account and account['details']:
                    for detail in account['details']:
                        if detail.get('ccy') == ccy:
                            avail_bal = detail.get('availBal', '0')
                            return float(avail_bal)
            
            logger.warning(f"Баланс {ccy} не найден")
            return 0.0
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении баланса: {e}")
            return 0.0
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при получении баланса: {e}")
            return 0.0
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Ошибка парсинга баланса {ccy}: {e}")
            return 0.0


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
            try:
                ticker_response = self.session.get(
                    self.base_url + ticker_path,
                    timeout=30,
                    verify=True
                )
                ticker_data = ticker_response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении тикера: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении тикера: {e}")
                raise
            
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
            try:
                books_response = self.session.get(
                    self.base_url + books_path,
                    timeout=30,
                    verify=True
                )
                books_data = books_response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении стакана: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении стакана: {e}")
                raise
            
            if 'data' in books_data and books_data['data']:
                result['order_book'] = {
                    'instId': books_data['data'][0].get('instId'),
                    'bids': books_data['data'][0].get('bids', [])[:3],
                    'asks': books_data['data'][0].get('asks', [])[:3],
                    'ts': books_data['data'][0].get('ts')
                }
            
            # 3. Только последние 10 свечей (вместо 288)
            candles_path = f'/api/v5/market/candles?instId={inst_id}&bar=5m&limit=10'
            try:
                candles_response = self.session.get(
                    self.base_url + candles_path,
                    timeout=30,
                    verify=True
                )
                candles_data = candles_response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении свечей: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении свечей: {e}")
                raise
            
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
            try:
                response = self.session.get(
                    self.base_url + path,
                    timeout=30,
                    verify=True
                )
                result = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении тикеров: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении тикеров: {e}")
                raise
            
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
            
            currencies_path = '/api/v5/asset/currencies'
            
            try:
                response = self.session.get(
                    self.base_url + currencies_path,
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении информации о валютах: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении информации о валютах: {e}")
                raise
            
            logger.info("Информация о валютах успешно получена")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о валютах: {e}")
            raise





    def get_balances(self) -> Dict:
        """
        Получение балансов всех валют
        
        Returns:
            Dict: Балансы по всем валютам
        """
        try:
            logger.info("Получение балансов всех валют")
            
            balances_path = '/api/v5/account/balance'
            
            try:
                response = self.session.get(
                    self.base_url + balances_path,
                    headers=self.get_auth_headers("GET", balances_path),
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении балансов: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении балансов: {e}")
                raise
            
            # Извлекаем балансы из ответа
            balances = {}
            if 'data' in data and data['data']:
                for account in data['data']:
                    if 'details' in account:
                        for detail in account['details']:
                            ccy = detail.get('ccy', '')
                            bal = detail.get('bal', '0')
                            if ccy and float(bal) > 0:
                                balances[ccy] = float(bal)
            
            result = {
                "success": True,
                "balances": balances,
                "message": "Баланс успешно получен"
            }
            
            logger.info(f"Балансы успешно получены: {balances}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения балансов: {e}")
            return {
                "success": False,
                "balances": {},
                "message": f"Ошибка получения балансов: {e}"
            }


    def get_orderbook(self, inst_id: str = "BTC-USDT", depth: int = 20) -> Dict:
        """
        Получение стакана ордеров
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            depth: Глубина стакана (по умолчанию 20)
            
        Returns:
            Dict: Стакан ордеров
        """
        try:
            logger.info(f"Получение стакана ордеров для {inst_id} с глубиной {depth}")
            
            path = f'/api/v5/market/books?instId={inst_id}&sz={depth}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении стакана: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении стакана: {e}")
                raise
            
            logger.info(f"Стакан ордеров для {inst_id} успешно получен")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения стакана ордеров: {e}")
            return {
                "code": "1",
                "msg": f"Ошибка получения стакана: {e}",
                "data": []
            }


    def get_current_candles(self, inst_id: str = "BTC-USDT", bar: str = "1m", limit: int = 100) -> Dict:
        """
        Получение текущих свечей
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            bar: Интервал свечей (1m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 12H, 1D, 1W, 1M, 3M, 6M, 1Y)
            limit: Количество свечей (по умолчанию 100)
            
        Returns:
            Dict: Текущие свечи
        """
        try:
            logger.info(f"Получение текущих свечей для {inst_id}, интервал {bar}, количество {limit}")
            
            path = f'/api/v5/market/candles?instId={inst_id}&bar={bar}&limit={limit}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении свечей: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении свечей: {e}")
                raise
            
            logger.info(f"Текущие свечи для {inst_id} успешно получены")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения текущих свечей: {e}")
            return {
                "code": "1",
                "msg": f"Ошибка получения свечей: {e}",
                "data": []
            }


    def get_history_candles(self, inst_id: str = "BTC-USDT", bar: str = "1m", limit: int = 1000) -> Dict:
        """
        Получение исторических свечей
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            bar: Интервал свечей
            limit: Количество свечей (по умолчанию 1000)
            
        Returns:
            Dict: Исторические свечи
        """
        try:
            logger.info(f"Получение исторических свечей для {inst_id}, интервал {bar}, количество {limit}")
            
            path = f'/api/v5/market/history-candles?instId={inst_id}&bar={bar}&limit={limit}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении исторических свечей: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении исторических свечей: {e}")
                raise
            
            logger.info(f"Исторические свечи для {inst_id} успешно получены")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения исторических свечей: {e}")
            return {
                "code": "1",
                "msg": f"Ошибка получения исторических свечей: {e}",
                "data": []
            }


    def get_active_orders(self, inst_id: str = "BTC-USDT") -> Dict:
        """
        Получение активных ордеров пользователя
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Активные ордера
        """
        try:
            logger.info(f"Получение активных ордеров для {inst_id}")
            
            path = f'/api/v5/trade/orders-pending?instId={inst_id}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    headers=self.get_auth_headers("GET", path),
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении активных ордеров: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении активных ордеров: {e}")
                raise
            
            logger.info(f"Активные ордера для {inst_id} успешно получены")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения активных ордеров: {e}")
            return {
                "code": "1",
                "msg": f"Ошибка получения активных ордеров: {e}",
                "data": []
            }


    def buy_btc_with_exits(
        self, 
        buy_amount: float, 
        inst_id: str = "BTC-USDT",
        limit_price: float = None,
        take_profit_percent: float = 5.0,
        stop_loss_percent: float = 2.0
    ) -> dict:
        """
        Покупка BTC в LIMIT с автоматическими точками выхода
        
        Args:
            buy_amount: Сумма в USDT для покупки
            inst_id: Инструмент (по умолчанию BTC-USDT)
            limit_price: Цена для LIMIT ордера
            take_profit_percent: Процент для Take Profit
            stop_loss_percent: Процент для Stop Loss
            
        Returns:
            dict: Результат операции с информацией о покупке и ордерах
        """
        try:
            logger.info(f"=== ПОКУПКА BTC С ТОЧКАМИ ВЫХОДА ===")
            logger.info(f"Сумма покупки: {buy_amount} USDT")
            logger.info(f"Инструмент: {inst_id}")
            logger.info(f"LIMIT цена: {limit_price}")
            logger.info(f"Take Profit: {take_profit_percent}%")
            logger.info(f"Stop Loss: {stop_loss_percent}%")
            
            # 1. Получаем текущую цену для расчета точек выхода
            ticker_data = self.get_ticker_data(inst_id)
            if not ticker_data.get("success", False):
                return {
                    "success": False,
                    "buy_amount": buy_amount,
                    "limit_price": limit_price,
                    "take_profit_price": 0,
                    "stop_loss_price": 0,
                    "buy_order": {"error": "Не удалось получить данные тикера"},
                    "take_profit_order": {"error": "Не удалось получить данные тикера"},
                    "stop_loss_order": {"error": "Не удалось получить данные тикера"},
                    "btc_acquired": 0,
                    "message": "Ошибка получения данных тикера"
                }
            
            current_price = float(ticker_data["data"]["last"])
            logger.info(f"Текущая цена: {current_price}")
            
            # 2. Рассчитываем цены для точек выхода
            take_profit_price = current_price * (1 + take_profit_percent / 100)
            stop_loss_price = current_price * (1 - stop_loss_percent / 100)
            
            logger.info(f"Take Profit цена: {take_profit_price}")
            logger.info(f"Stop Loss цена: {stop_loss_price}")
            
            # 3. Покупаем BTC по LIMIT цене
            buy_result = self.place_limit_order(
                inst_id=inst_id,
                side="buy",
                size=buy_amount,
                price=limit_price
            )
            
            if buy_result.get("code") != "0":
                return {
                    "success": False,
                    "buy_amount": buy_amount,
                    "limit_price": limit_price,
                    "take_profit_price": take_profit_price,
                    "stop_loss_price": stop_loss_price,
                    "buy_order": buy_result,
                    "take_profit_order": {"error": "Покупка не удалась"},
                    "stop_loss_order": {"error": "Покупка не удалась"},
                    "btc_acquired": 0,
                    "message": f"Ошибка покупки: {buy_result.get('msg', 'Неизвестная ошибка')}"
                }
            
            # 4. Получаем количество купленного BTC
            btc_acquired = buy_amount / limit_price
            
            # 5. Устанавливаем Take Profit ордер
            take_profit_result = self.place_limit_order(
                inst_id=inst_id,
                side="sell",
                size=btc_acquired,
                price=take_profit_price
            )
            
            # 6. Устанавливаем Stop Loss ордер
            stop_loss_result = self.place_limit_order(
                inst_id=inst_id,
                side="sell", 
                size=btc_acquired,
                price=stop_loss_price
            )
            
            # 7. Формируем ответ
            success = (
                buy_result.get("code") == "0" and
                take_profit_result.get("code") == "0" and
                stop_loss_result.get("code") == "0"
            )
            
            message = (
                f"BTC успешно куплен на {buy_amount} USDT по цене {limit_price} "
                f"с TP {take_profit_price} и SL {stop_loss_price}"
            )
            
            if not success:
                message = "Покупка выполнена, но не все ордера установлены"
            
            logger.info(f"Результат: {message}")
            
            return {
                "success": success,
                "buy_amount": buy_amount,
                "limit_price": limit_price,
                "take_profit_price": take_profit_price,
                "stop_loss_price": stop_loss_price,
                "buy_order": buy_result,
                "take_profit_order": take_profit_result,
                "stop_loss_order": stop_loss_result,
                "btc_acquired": btc_acquired,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Ошибка покупки BTC с точками выхода: {e}")
            return {
                "success": False,
                "buy_amount": buy_amount,
                "limit_price": limit_price if limit_price else 0,
                "take_profit_price": 0,
                "stop_loss_price": 0,
                "buy_order": {"error": str(e)},
                "take_profit_order": {"error": str(e)},
                "stop_loss_order": {"error": str(e)},
                "btc_acquired": 0,
                "message": f"Ошибка покупки BTC: {str(e)}"
            }


    def place_limit_order(
        self, 
        inst_id: str, 
        side: str, 
        size: float, 
        price: float
    ) -> dict:
        """
        Размещение LIMIT ордера
        
        Args:
            inst_id: Инструмент
            side: Сторона (buy/sell)
            size: Размер (в USDT для покупки, в BTC для продажи)
            price: Цена
            
        Returns:
            dict: Результат размещения ордера
        """
        try:
            # Определяем размер в BTC
            if side == "buy":
                # Для покупки size в USDT, нужно перевести в BTC
                btc_size = size / price
            else:
                # Для продажи size уже в BTC
                btc_size = size
            
            body = {
                "instId": inst_id,
                "tdMode": "cash",
                "side": side,
                "ordType": "limit",
                "sz": str(btc_size),
                "px": str(price)
            }
            
            logger.info(f"{side.upper()} LIMIT BODY: {body}")
            
            # Генерируем заголовки авторизации
            headers = self.get_auth_headers("POST", "/api/v5/trade/order", body)
            
            # Выполняем запрос
            response = requests.post(
                f"{self.base_url}/api/v5/trade/order",
                headers=headers,
                json=body,
                timeout=10
            )
            
            result = response.json()
            logger.info(f"{side.upper()} LIMIT ORDER RESULT: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка размещения LIMIT ордера: {e}")
            return {"error": str(e)}


    def get_ticker_data(self, inst_id: str = "BTC-USDT") -> dict:
        """
        Получение данных тикера
        
        Args:
            inst_id: Инструмент
            
        Returns:
            dict: Данные тикера
        """
        try:
            logger.info(f"Получение данных тикера для {inst_id}")
            
            path = f'/api/v5/market/ticker?instId={inst_id}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    timeout=30,
                    verify=True
                )
                result = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении тикера: {e}")
                return {"success": False, "error": f"SSL ошибка: {e}"}
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении тикера: {e}")
                return {"success": False, "error": f"Ошибка сети: {e}"}
            
            logger.info(f"TICKER DATA RESULT: {result}")
            
            # Проверяем успешность запроса
            if result.get("code") == "0" and result.get("data") and len(result["data"]) > 0:
                return {"success": True, "data": result["data"][0]}
            else:
                logger.error(f"Ошибка API тикера: {result}")
                return {"success": False, "error": result.get("msg", "Неизвестная ошибка")}
            
        except Exception as e:
            logger.error(f"Ошибка получения данных тикера: {e}")
            return {"success": False, "error": str(e)}


    def get_market_analytics(self, inst_id: str = "BTC-USDT") -> Dict:
        """
        Получение полных аналитических данных для n8n
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Полные аналитические данные
        """
        try:
            logger.info(f"=== НАЧАЛО ПОЛУЧЕНИЯ АНАЛИТИКИ ДЛЯ {inst_id} ===")
            
            # Получаем все данные параллельно
            orderbook = self.get_orderbook(inst_id)
            current_candles = self.get_current_candles(inst_id)
            history_candles = self.get_history_candles(inst_id)
            active_orders = self.get_active_orders(inst_id)
            balances = self.get_balances()
            ticker = self.get_ticker_data(inst_id)
            
            # Формируем ответ
            result = {
                "success": True,
                "inst_id": inst_id,
                "market_data": {
                    "orderbook": orderbook.get("data", []),
                    "current_candles": current_candles.get("data", []),
                    "history_candles": history_candles.get("data", [])
                },
                "user_data": {
                    "active_orders": active_orders.get("data", []),
                    "balances": balances.get("balances", {})
                },
                "indicators": {
                    "current_price": "0",
                    "volume_24h": "0",
                    "change_24h": "0",
                    "high_24h": "0",
                    "low_24h": "0"
                },
                "timestamp": self.get_server_timestamp(),
                "message": "Аналитические данные успешно получены"
            }
            
            # Извлекаем индикаторы из тикера
            if ticker.get("data") and ticker["data"]:
                ticker_data = ticker["data"][0]
                result["indicators"] = {
                    "current_price": ticker_data.get("last", "0"),
                    "volume_24h": ticker_data.get("vol24h", "0"),
                    "change_24h": ticker_data.get("change24h", "0"),
                    "high_24h": ticker_data.get("high24h", "0"),
                    "low_24h": ticker_data.get("low24h", "0")
                }
            
            logger.info(f"=== АНАЛИТИКА ЗАВЕРШЕНА ДЛЯ {inst_id} ===")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения аналитических данных: {e}")
            return {
                "success": False,
                "inst_id": inst_id,
                "market_data": {"orderbook": [], "current_candles": [], "history_candles": []},
                "user_data": {"active_orders": [], "balances": {}},
                "indicators": {"current_price": "0", "volume_24h": "0", "change_24h": "0", "high_24h": "0", "low_24h": "0"},
                "timestamp": self.get_server_timestamp(),
                "message": f"Ошибка получения аналитических данных: {e}"
            }


# Глобальный экземпляр сервиса
okx_service = OKXService() 