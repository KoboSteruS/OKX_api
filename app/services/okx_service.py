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
import json

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
        body: str = "",
        demo: bool = False
    ) -> Dict[str, str]:
        """
        Получение заголовков авторизации для OKX API
        
        Args:
            method: HTTP метод
            request_path: Путь запроса
            body: Тело запроса
            demo: Режим демо-трейдинга (True для симуляции)
            
        Returns:
            Dict[str, str]: Заголовки авторизации
        """
        try:
            timestamp = self.get_server_timestamp()
            signature = self.generate_signature(timestamp, method, request_path, body)
            mode = "1" if demo else "0"  # '1' для демо (симуляция), '0' для реального
            
            headers = {
                'OK-ACCESS-KEY': self.api_key.strip(),
                'OK-ACCESS-SIGN': signature.strip(),
                'OK-ACCESS-TIMESTAMP': timestamp.strip(),
                'OK-ACCESS-PASSPHRASE': self.passphrase.strip(),
                'Content-Type': 'application/json',
                'x-simulated-trading': mode  # Демо режим
            }
            
            logger.info(f"Сгенерированы заголовки авторизации для {method} {request_path} (demo: {demo})")
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


    def place_market_order(self, side: str, notional: float, inst_id: str = "BTC-USDT", demo: bool = False) -> Dict:
        """
        Размещение рыночного ордера
        
        Args:
            side: Сторона (buy/sell)
            notional: Размер в USDT для покупки или BTC для продажи
            inst_id: Инструмент для торговли (по умолчанию BTC-USDT)
            demo: Режим демо-трейдинга
            
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
        
        headers = self.get_auth_headers("POST", path, body_str, demo=demo)
        
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


    def place_market_sell_order(self, amount_btc: float, inst_id: str = "BTC-USDT", demo: bool = False) -> Dict:
        """
        Продажа BTC по рыночной цене (market order)

        Args:
            amount_btc: Количество BTC для продажи
            inst_id: Торговая пара (по умолчанию BTC-USDT)
            demo: Демо-режим

        Returns:
            Dict: Результат размещения ордера
        """
        import json
        path = '/api/v5/trade/order'
        url = self.base_url + path

        body = {
            "instId": inst_id,
            "tdMode": "cash",
            "side": "sell",
            "ordType": "market",
            "sz": str(amount_btc)  # всегда в BTC
        }

        body_str = json.dumps(body, separators=(",", ":"))
        logger.info(f"SELL MARKET BODY: {body_str}")

        headers = self.get_auth_headers("POST", path, body_str, demo=demo)

        try:
            response = self.session.post(
                url,
                headers=headers,
                data=body_str,
                timeout=30,
                verify=True
            )
            logger.info(f"SELL MARKET ORDER RESULT: {response.text}")
            return response.json()
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL ошибка при размещении ордера: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при размещении ордера: {e}")
            raise
    
    def get_balance(self, ccy: str, demo: bool = False) -> float:
        """
        Получение баланса валюты
        
        Args:
            ccy: Код валюты (BTC, USDT, etc.)
            demo: Режим демо-трейдинга
            
        Returns:
            float: Доступный баланс
        """
        path = f'/api/v5/account/balance?ccy={ccy}'
        url = self.base_url + path
        
        headers = self.get_auth_headers("GET", path, demo=demo)
        
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


    def sell_btc_market(self, sell_amount: float, inst_id: str = "BTC-USDT", demo: bool = False) -> Dict:
        """
        Обёртка для продажи BTC в маркет
        """
        logger.info(f"Продажа BTC в маркет: {sell_amount} BTC (demo: {demo})")

        result = self.place_market_sell_order(
            amount_btc=sell_amount,
            inst_id=inst_id,
            demo=demo
        )

        return {
            "success": result.get("code") == "0",
            "sell_amount": sell_amount,
            "sell_order": result,
            "message": "Продажа BTC выполнена" if result.get("code") == "0" else f"Ошибка продажи: {result}"
        }



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


    def cancel_order(self, inst_id: str, ord_id: str, demo: bool = False) -> Dict:
        """
        Отмена ордера по ID и инструменту

        Returns:
            Dict: Результат отмены
        """
        try:
            logger.info(f"Попытка отменить ордер {ord_id} на инструменте {inst_id}")

            path = "/api/v5/trade/cancel-order"
            payload = {
                "instId": inst_id,
                "ordId": ord_id
            }

            body_str = json.dumps(payload)
            response = self.session.post(
                self.base_url + path,
                headers=self.get_auth_headers("POST", path, body=body_str, demo=demo),
                json=payload,
                timeout=30,
                verify=True
            )

            data = response.json()
            logger.debug(f"Ответ от OKX при отмене ордера: {json.dumps(data, indent=2, ensure_ascii=False)}")

            cancelled = data.get("data", [{}])[0]

            return {
                "success": True,
                "message": "Ордер успешно отменён",
                "cancelled_order": cancelled
            }

        except Exception as e:
            logger.error(f"Ошибка отмены ордера: {e}")
            return {
                "success": False,
                "cancelled_order": {},
                "message": f"Ошибка отмены ордера: {e}"
            }


    def get_orders(self, demo: bool = False) -> Dict:
        """
        Получение всех открытых ордеров

        Returns:
            Dict: Список ордеров и статус выполнения
        """
        try:
            logger.info("Получение открытых ордеров")

            orders_path = '/api/v5/trade/orders-pending'

            try:
                response = self.session.get(
                    self.base_url + orders_path,
                    headers=self.get_auth_headers("GET", orders_path, demo=demo),
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении ордеров: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении ордеров: {e}")
                raise

            logger.debug(f"Сырой JSON ордеров от OKX: {json.dumps(data, indent=2, ensure_ascii=False)}")

            orders = data.get("data", [])

            result = {
                "success": True,
                "orders": orders,
                "message": "Ордера успешно получены"
            }

            logger.info(f"Открытых ордеров: {len(orders)}")
            return result

        except Exception as e:
            logger.error(f"Ошибка получения ордеров: {e}")
            return {
                "success": False,
                "orders": [],
                "message": f"Ошибка получения ордеров: {e}"
            }


    def get_trade_fills(
        self,
        inst_type: Optional[str] = None,
        inst_id: Optional[str] = None,
        ord_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: int = 100,
        demo: bool = False
    ) -> Dict:
        """
        Получение последних сделок (заполненных ордеров)
        
        Args:
            inst_type: Тип инструмента (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            inst_id: Инструмент (например, BTC-USDT)
            ord_id: ID ордера
            after: Курсор пагинации (ID сделки, после которой запрашиваются данные)
            before: Курсор пагинации (ID сделки, до которой запрашиваются данные)
            limit: Количество записей (по умолчанию 100, максимум 100)
            demo: Режим демо-трейдинга
            
        Returns:
            Dict: Список последних сделок и статус выполнения
        """
        try:
            logger.info(f"Получение последних сделок с параметрами: inst_type={inst_type}, inst_id={inst_id}, ord_id={ord_id}, after={after}, before={before}, limit={limit}")
            
            path = '/api/v5/trade/fills'
            params = {}
            
            # Формируем параметры запроса, исключая None
            if inst_type:
                params['instType'] = inst_type
            if inst_id:
                params['instId'] = inst_id
            if ord_id:
                params['ordId'] = ord_id
            if after:
                params['after'] = after
            if before:
                params['before'] = before
            if limit:
                params['limit'] = str(limit)
            
            # Формируем query string для подписи
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()]) if params else ''
            request_path = f"{path}?{query_string}" if query_string else path
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    headers=self.get_auth_headers("GET", request_path, demo=demo),
                    params=params,
                    timeout=30,
                    verify=True
                )
                data = response.json()
            except requests.exceptions.SSLError as e:
                logger.error(f"SSL ошибка при получении сделок: {e}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка сети при получении сделок: {e}")
                raise
            
            logger.debug(f"Сырой JSON сделок от OKX: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            fills = data.get("data", [])
            
            result = {
                "success": True,
                "fills": fills,
                "message": f"Получено {len(fills)} сделок"
            }
            
            logger.info(f"Последние сделки успешно получены: {len(fills)} записей")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения последних сделок: {e}")
            return {
                "success": False,
                "fills": [],
                "message": f"Ошибка получения сделок: {e}"
            }


    def get_balances(self, demo: bool = False) -> Dict:
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
                    headers=self.get_auth_headers("GET", balances_path, demo=demo),
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

            # Лог сырого ответа
            logger.debug(f"Сырой JSON от OKX: {json.dumps(data, indent=2, ensure_ascii=False)}")

            # Извлекаем балансы
            balances = {}
            if 'data' in data and data['data']:
                for account in data['data']:
                    if 'details' in account:
                        for detail in account['details']:
                            ccy = detail.get('ccy', '')
                            bal = detail.get('cashBal') or detail.get('availBal') or detail.get('eq') or '0'
                            try:
                                if ccy and float(bal) > 0:
                                    balances[ccy] = float(bal)
                            except ValueError:
                                logger.warning(f"Невозможно преобразовать баланс {bal} для валюты {ccy}")

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


    def get_active_orders(self, inst_id: str = "BTC-USDT", demo: bool = False) -> Dict:
        """
        Получение активных ордеров пользователя
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            demo: Режим демо-трейдинга
            
        Returns:
            Dict: Активные ордера
        """
        try:
            logger.info(f"Получение активных ордеров для {inst_id}")
            
            path = f'/api/v5/trade/orders-pending?instId={inst_id}'
            
            try:
                response = self.session.get(
                    self.base_url + path,
                    headers=self.get_auth_headers("GET", path, demo=demo),
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
            take_profit_percent: float = 0.5,
            stop_loss_percent: float = 0.2,
            demo: bool = False
        ) -> dict:
        """
        Покупка BTC с автоматическими точками выхода

        Args:
            buy_amount: Сумма в USDT для покупки
            inst_id: Инструмент (по умолчанию BTC-USDT)
            take_profit_percent: Процент для Take Profit
            stop_loss_percent: Процент для Stop Loss
            demo: Режим демо-трейдинга

        Returns:
            dict: Результат операции с информацией о покупке и ордерах
        """
        try:
            logger.info("=== ПОКУПКА BTC С ТОЧКАМИ ВЫХОДА ===")
            logger.info(f"Сумма покупки: {buy_amount} USDT")
            logger.info(f"Инструмент: {inst_id}")
            logger.info(f"Take Profit: {take_profit_percent}%")
            logger.info(f"Stop Loss: {stop_loss_percent}%")
            logger.info(f"Demo mode: {demo}")

            # 1. Получаем BTC баланс до покупки
            btc_before = self.get_balance("BTC", demo=demo)
            logger.info(f"Баланс BTC до покупки: {btc_before}")

            # 2. Покупаем BTC по рыночной цене
            buy_result = self.place_market_order("buy", buy_amount, inst_id, demo=demo)
            logger.info(f"Buy result: {buy_result}")
            if buy_result.get("code") != "0":
                return {
                    "success": False,
                    "buy_amount": buy_amount,
                    "current_price": 0,
                    "take_profit_price": 0,
                    "stop_loss_price": 0,
                    "buy_order": buy_result,
                    "take_profit_order": {"error": "Покупка не удалась"},
                    "stop_loss_order": {"error": "Покупка не удалась"},
                    "btc_acquired": 0,
                    "message": f"Ошибка покупки: {buy_result.get('msg', 'Неизвестная ошибка')}"
                }

            # 3. Получаем BTC баланс после покупки
            btc_after = self.get_balance("BTC", demo=demo)
            logger.info(f"Баланс BTC после покупки: {btc_after}")

            # 4. Считаем, сколько BTC реально получили
            btc_acquired = btc_after - btc_before
            logger.info(f"Получено BTC: {btc_acquired}")

            if btc_acquired <= 0:
                raise ValueError("BTC не был получен после покупки.")

            # 5. Вычисляем фактическую цену покупки
            actual_price = buy_amount / btc_acquired
            logger.info(f"Фактическая цена покупки: {actual_price}")

            # 6. Рассчитываем TP и SL
            take_profit_price = actual_price * (1 + take_profit_percent / 100)
            stop_loss_price = actual_price * (1 - stop_loss_percent / 100)
            logger.info(f"Рассчитанный Take Profit: {take_profit_price}")
            logger.info(f"Рассчитанный Stop Loss: {stop_loss_price}")

            # 7. Устанавливаем Take Profit ордер (limit)
            take_profit_result = self.place_limit_order(
                inst_id=inst_id,
                side="sell",
                size=btc_acquired,
                price=take_profit_price,
                demo=demo
            )

            # 8. Устанавливаем Stop Loss ордер (trigger)
            stop_loss_result = self.place_stop_loss_order(
                inst_id=inst_id,
                size=btc_acquired,
                trigger_price=stop_loss_price,
                demo=demo
            )

            # 9. Финальный статус
            success = (
                buy_result.get("code") == "0" and
                take_profit_result.get("code") == "0" and
                stop_loss_result.get("code") == "0"
            )

            if success:
                message = (
                    f"BTC успешно куплен на {buy_amount} USDT по цене {actual_price} "
                    f"с TP {take_profit_price} и SL {stop_loss_price}"
                )
            else:
                message = "Покупка выполнена, но не все ордера установлены"

            logger.info(f"Результат: {message}")

            return {
                "success": success,
                "buy_amount": buy_amount,
                "current_price": actual_price,
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
                "current_price": 0,
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
        price: float,
        demo: bool = False
    ) -> dict:
        """
        Размещение LIMIT ордера
        
        Args:
            inst_id: Инструмент
            side: Сторона (buy/sell)
            size: Размер в BTC (для всех типов ордеров)
            price: Цена
            demo: Режим демо-трейдинга
            
        Returns:
            dict: Результат размещения ордера
        """
        try:
            # Размер уже в BTC для всех типов ордеров
            btc_size = size
            
            body = {
                "instId": inst_id,
                "tdMode": "cash",
                "side": side,
                "ordType": "limit",
                "sz": str(btc_size),
                "px": str(price)
            }
            
            import json
            body_str = json.dumps(body, separators=(",", ":"))
            logger.info(f"{side.upper()} LIMIT BODY: {body_str}")
            
            # Генерируем заголовки авторизации
            headers = self.get_auth_headers("POST", "/api/v5/trade/order", body_str, demo=demo)
            logger.info(f"{side.upper()} LIMIT HEADERS: {headers}")
            
            # Выполняем запрос
            response = self.session.post(
                f"{self.base_url}/api/v5/trade/order",
                headers=headers,
                data=body_str,
                timeout=10
            )
            
            result = response.json()
            logger.info(f"{side.upper()} LIMIT ORDER RESULT: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка размещения LIMIT ордера: {e}")
            return {"error": str(e)}


    def place_stop_loss_order(
        self, 
        inst_id: str, 
        size: float, 
        trigger_price: float,
        demo: bool = False
    ) -> dict:
        """
        Размещение Stop Loss ордера через algo order
        
        Args:
            inst_id: Инструмент
            size: Размер в BTC
            trigger_price: Цена активации (stop price)
            demo: Режим демо-трейдинга
            
        Returns:
            dict: Результат размещения ордера
        """
        try:
            body = {
                "instId": inst_id,
                "tdMode": "cash",
                "side": "sell",
                "ordType": "trigger",
                "triggerPx": str(trigger_price),  # Триггер-цена
                "triggerPxType": "last",          # Тип цены
                "orderPx": str(trigger_price),    # Цена исполнения ордера
                "sz": str(size)
            }
            
            import json
            body_str = json.dumps(body, separators=(",", ":"))
            logger.info(f"STOP LOSS BODY: {body_str}")
            
            # Генерируем заголовки авторизации
            headers = self.get_auth_headers("POST", "/api/v5/trade/order-algo", body_str, demo=demo)
            logger.info(f"STOP LOSS HEADERS: {headers}")
            
            # Выполняем запрос
            response = self.session.post(
                f"{self.base_url}/api/v5/trade/order-algo",
                headers=headers,
                data=body_str,
                timeout=10
            )
            
            result = response.json()
            logger.info(f"STOP LOSS ORDER RESULT: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка создания Stop Loss ордера: {e}")
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


    def get_market_analytics(
        self, 
        inst_id: str = "BTC-USDT",
        bar: str = "1m",
        depth: int = 20,
        current_limit: int = 100,
        history_limit: int = 1000,
        demo: bool = False
    ) -> Dict:
        """
        Получение полных аналитических данных для n8n
        
        Args:
            inst_id: Инструмент (по умолчанию BTC-USDT)
            bar: Интервал свечей (по умолчанию 1m)
            depth: Глубина стакана (по умолчанию 20)
            current_limit: Количество текущих свечей (по умолчанию 100)
            history_limit: Количество исторических свечей (по умолчанию 1000)
            demo: Режим демо-трейдинга
            
        Returns:
            Dict: Полные аналитические данные
        """
        try:
            logger.info(f"=== НАЧАЛО ПОЛУЧЕНИЯ АНАЛИТИКИ ДЛЯ {inst_id} ===")
            logger.info(f"Параметры: bar={bar}, depth={depth}, current_limit={current_limit}, history_limit={history_limit}, demo={demo}")
            
            # Получаем все данные с указанными параметрами
            logger.info("Получение orderbook...")
            orderbook = self.get_orderbook(inst_id, depth)
            logger.info(f"Orderbook получен: {len(orderbook.get('data', []))} записей")
            
            logger.info("Получение current_candles...")
            current_candles = self.get_current_candles(inst_id, bar, current_limit)
            logger.info(f"Current candles получены: {len(current_candles.get('data', []))} записей")
            
            logger.info("Получение history_candles...")
            history_candles = self.get_history_candles(inst_id, bar, history_limit)
            logger.info(f"History candles получены: {len(history_candles.get('data', []))} записей")
            
            logger.info("Получение active_orders...")
            active_orders = self.get_active_orders(inst_id, demo=demo)
            logger.info(f"Active orders получены: {len(active_orders.get('data', []))} записей")
            
            logger.info("Получение balances...")
            balances = self.get_balances(demo=demo)
            logger.info(f"Balances получены: {len(balances.get('balances', {}))} валют")
            
            logger.info("Получение ticker...")
            ticker = self.get_ticker_data(inst_id)
            logger.info(f"Ticker получен: {ticker.get('success', False)}")
            
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
            if ticker.get("success") and ticker.get("data"):
                # Проверяем, что data - это список
                if isinstance(ticker["data"], list) and len(ticker["data"]) > 0:
                    ticker_data = ticker["data"][0]
                else:
                    # Если data - это не список, используем его напрямую
                    ticker_data = ticker["data"]
                
                result["indicators"] = {
                    "current_price": ticker_data.get("last", "0"),
                    "volume_24h": ticker_data.get("vol24h", "0"),
                    "change_24h": ticker_data.get("change24h", "0"),
                    "high_24h": ticker_data.get("high24h", "0"),
                    "low_24h": ticker_data.get("low24h", "0")
                }
                logger.info(f"Индикаторы извлечены: {result['indicators']}")
            else:
                logger.warning(f"Ticker не содержит данных: {ticker}")
            
            logger.info(f"=== АНАЛИТИКА ЗАВЕРШЕНА ДЛЯ {inst_id} ===")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения аналитических данных: {e}")
            logger.error(f"Тип ошибки: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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