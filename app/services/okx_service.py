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
        headers['x-simulated-trading'] = '1'  # Демо режим
        
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
        headers['x-simulated-trading'] = '1'  # Демо режим
        
        try:
            response = self.session.get(
                url, 
                headers=headers,
                timeout=30,
                verify=True
            )
            data = response.json()
            return float(data['data'][0]['details'][0]['availBal'])
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при получении баланса: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при получении баланса: {e}")
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


    def buy_btc(self, buy_amount: float, inst_id: str = "BTC-USDT") -> Dict:
        """
        Покупка BTC на указанную сумму USDT
        
        Args:
            buy_amount: Сумма в USDT для покупки BTC
            inst_id: Инструмент для покупки (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Результат покупки с информацией о приобретенном BTC
        """
        try:
            logger.info(f"=== НАЧАЛО ПОКУПКИ BTC ===")
            logger.info(f"Сумма покупки: {buy_amount} USDT")
            logger.info(f"Инструмент: {inst_id}")
            
            # Покупка BTC на указанную сумму USDT
            buy_result = self.place_market_order("buy", notional=buy_amount, inst_id=inst_id)
            
            # Получаем баланс BTC для определения количества приобретенного BTC
            btc_balance = self.get_balance("BTC")
            
            result = {
                "success": True,
                "buy_amount": buy_amount,
                "buy_order": buy_result,
                "btc_acquired": btc_balance,
                "message": f"BTC успешно куплен на {buy_amount} USDT"
            }
            
            logger.info(f"=== ПОКУПКА ЗАВЕРШЕНА ===")
            logger.info(f"Результат: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка покупки BTC: {e}")
            return {
                "success": False,
                "buy_amount": buy_amount,
                "buy_order": {"error": str(e)},
                "btc_acquired": 0.0,
                "message": f"Ошибка покупки BTC: {e}"
            }


    def sell_btc(self, sell_all: bool = True, sell_amount: Optional[float] = None, inst_id: str = "BTC-USDT") -> Dict:
        """
        Продажа BTC
        
        Args:
            sell_all: Продать весь доступный BTC (по умолчанию True)
            sell_amount: Количество BTC для продажи (если sell_all=False)
            inst_id: Инструмент для продажи (по умолчанию BTC-USDT)
            
        Returns:
            Dict: Результат продажи с информацией о полученных USDT
        """
        try:
            logger.info(f"=== НАЧАЛО ПРОДАЖИ BTC ===")
            logger.info(f"Продать все: {sell_all}")
            if not sell_all and sell_amount:
                logger.info(f"Количество для продажи: {sell_amount} BTC")
            logger.info(f"Инструмент: {inst_id}")
            
            # Получаем текущий баланс BTC
            btc_balance = self.get_balance("BTC")
            
            if btc_balance <= 0:
                return {
                    "success": False,
                    "sell_order": {"error": "Нет доступного BTC для продажи"},
                    "btc_sold": 0.0,
                    "usdt_received": 0.0,
                    "message": "Нет доступного BTC для продажи"
                }
            
            # Определяем количество BTC для продажи
            if sell_all:
                amount_to_sell = btc_balance
            else:
                if not sell_amount or sell_amount <= 0:
                    return {
                        "success": False,
                        "sell_order": {"error": "Неверное количество BTC для продажи"},
                        "btc_sold": 0.0,
                        "usdt_received": 0.0,
                        "message": "Неверное количество BTC для продажи"
                    }
                amount_to_sell = min(sell_amount, btc_balance)
            
            # Продажа BTC
            sell_result = self.place_market_order("sell", notional=amount_to_sell, inst_id=inst_id)
            
            # Получаем обновленный баланс USDT для определения полученной суммы
            usdt_balance_after = self.get_balance("USDT")
            
            result = {
                "success": True,
                "sell_order": sell_result,
                "btc_sold": amount_to_sell,
                "usdt_received": usdt_balance_after,
                "message": f"BTC успешно продан за {usdt_balance_after} USDT"
            }
            
            logger.info(f"=== ПРОДАЖА ЗАВЕРШЕНА ===")
            logger.info(f"Результат: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка продажи BTC: {e}")
            return {
                "success": False,
                "sell_order": {"error": str(e)},
                "btc_sold": 0.0,
                "usdt_received": 0.0,
                "message": f"Ошибка продажи BTC: {e}"
            }


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


# Глобальный экземпляр сервиса
okx_service = OKXService() 