# OKX Trading Bot

FastAPI приложение для автоматической торговли на OKX в демо-режиме.

## Описание

Это приложение предоставляет REST API для выполнения автоматических торговых стратегий на OKX API в демо-режиме.

## Возможности

- ✅ Автоматическая торговая стратегия
- ✅ Покупка BTC на 100 USDT
- ✅ Настраиваемое время ожидания
- ✅ Продажа всего доступного BTC
- ✅ Демо-режим (симуляция)
- ✅ Подробное логирование
- ✅ Автоматическая документация API
- ✅ Проверка здоровья сервиса

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd OKX
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации

Скопируйте файл конфигурации:
```bash
copy env.example .env
```

Отредактируйте `.env` файл, указав ваши ключи OKX API:
```env
# Настройки приложения
DEBUG=false

# OKX API настройки
OKX_API_KEY=your_api_key_here
OKX_API_SECRET=your_api_secret_here
OKX_PASSPHRASE=your_passphrase_here
OKX_BASE_URL=https://www.okx.com
```

## Запуск

### Разработка

```bash
python -m app.main
```

### Продакшн

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

## API Документация

После запуска приложения доступна автоматическая документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Использование API

### 1. Тестирование соединения с OKX API

```bash
curl "http://localhost:8000/api/v1/test-connection"
```

Проверяет соединение с OKX API и диагностирует проблемы SSL/TLS.

### 2. Выполнение торговой стратегии (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/trade" \
  -H "Content-Type: application/json" \
  -d '{"wait_minutes": 5, "buy_amount": 10.0}'
```

### 3. Выполнение торговой стратегии (GET)

```bash
curl "http://localhost:8000/api/v1/trade?wait_minutes=3&buy_amount=15.0"
```

### 4. Получение упрощенных рыночных данных (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/market-data" \
  -H "Content-Type: application/json" \
  -d '{"inst_id": "BTC-USDT"}'
```

### 5. Получение упрощенных рыночных данных (GET)

```bash
curl "http://localhost:8000/api/v1/market-data?inst_id=BTC-USDT"
```

**Включает**: тикер, стакан ордеров (3 уровня), последние 10 свечей

### 6. Получение данных всех тикеров (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/tickers" \
  -H "Content-Type: application/json" \
  -d '{"inst_type": "SPOT"}'
```

### 7. Получение данных всех тикеров (GET)

```bash
curl "http://localhost:8000/api/v1/tickers?inst_type=SWAP"
```

### 8. Получение информации о валютах

```bash
curl "http://localhost:8000/api/v1/currencies"
```

### 9. Проверка здоровья сервиса

```bash
curl "http://localhost:8000/api/v1/health"
```

### 10. Покупка BTC (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/buy" \
  -H "Content-Type: application/json" \
  -d '{"buy_amount": 10.0, "inst_id": "BTC-USDT"}'
```

### 11. Покупка BTC (GET)

```bash
curl "http://localhost:8000/api/v1/buy?buy_amount=15.0&inst_id=BTC-USDT"
```

### 12. Продажа BTC (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/sell" \
  -H "Content-Type: application/json" \
  -d '{"sell_all": true, "inst_id": "BTC-USDT"}'
```

### 13. Продажа BTC (GET)

```bash
curl "http://localhost:8000/api/v1/sell?sell_all=true&inst_id=BTC-USDT"
```

### 14. Получение балансов

```bash
curl "http://localhost:8000/api/v1/balance"
```

## ⚠️ Важно: Торговая стратегия

Приложение поддерживает два режима торговли:

### 1. Автоматическая торговая стратегия (устаревший режим)

Выполняет **автоматическую торговую стратегию** в демо-режиме:

1. **Покупка**: BTC на указанную сумму USDT (по умолчанию 10.0 USDT)
2. **Ожидание**: Указанное количество минут
3. **Продажа**: Весь доступный BTC

**Эндпоинт**: `/api/v1/trade`

### 2. Разделенные операции (рекомендуемый режим)

Для интеграции с n8n и другими системами автоматизации:

- **Покупка**: `/api/v1/buy` - покупка BTC на указанную сумму USDT
- **Продажа**: `/api/v1/sell` - продажа BTC за USDT
- **Баланс**: `/api/v1/balance` - получение балансов всех валют

**Преимущества**:
- Контроль времени ожидания в n8n
- Независимое выполнение операций
- Лучшая обработка ошибок
- Гибкость в настройке стратегий

**Демо-режим**: Все операции выполняются в симуляционном режиме (`x-simulated-trading: 1`)

**Параметры**:
- `buy_amount`: Сумма в USDT для покупки BTC (больше 0, по умолчанию 10.0)
- `sell_all`: Продать весь доступный BTC (по умолчанию True)
- `sell_amount`: Количество BTC для продажи (если sell_all=False)
- `inst_id`: Инструмент для торговли (по умолчанию BTC-USDT)

## Примеры ответов

### Успешное выполнение стратегии

```json
{
  "strategy_completed": true,
  "wait_minutes": 5,
  "buy_amount": 10.0,
  "buy_order": {
    "code": "0",
    "data": [{"ordId": "2724253814203600896", "sMsg": "Order placed"}]
  },
  "sell_order": {
    "code": "0",
    "data": [{"ordId": "2724263944018186240", "sMsg": "Order placed"}]
  },
  "btc_balance_sold": 0.001234
}
```

### Ответ с ошибкой

```json
{
  "error": "API_SECRET не настроен",
  "detail": "Проверьте настройки в .env файле"
}
```

### Успешная покупка BTC

```json
{
  "success": true,
  "buy_amount": 10.0,
  "buy_order": {
    "code": "0",
    "data": [{"ordId": "2724253814203600896", "sMsg": "Order placed"}]
  },
  "btc_acquired": 0.001234,
  "message": "BTC успешно куплен на 10.0 USDT"
}
```

### Успешная продажа BTC

```json
{
  "success": true,
  "sell_order": {
    "code": "0",
    "data": [{"ordId": "2724263944018186240", "sMsg": "Order placed"}]
  },
  "btc_sold": 0.001234,
  "usdt_received": 10.5,
  "message": "BTC успешно продан за 10.5 USDT"
}
```

### Получение балансов

```json
{
  "success": true,
  "balances": {
    "BTC": 0.001234,
    "USDT": 89.5
  },
  "message": "Баланс успешно получен"
}
```

## Структура проекта

```
OKX/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Основное приложение
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints.py        # API эндпоинты
│   │   └── schemas.py          # Pydantic схемы
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Конфигурация
│   │   └── logger.py           # Настройка логирования
│   └── services/
│       ├── __init__.py
│       └── okx_service.py      # Сервис для работы с OKX API
├── logs/                       # Логи приложения
├── requirements.txt            # Зависимости
├── env.example                 # Пример конфигурации
└── README.md                   # Документация
```

## Логирование

Приложение использует `loguru` для логирования. Логи сохраняются в:

- **Консоль**: Цветной вывод с временными метками
- **Файл**: `logs/app.log` с ротацией (10 MB, 7 дней)

## Безопасность

⚠️ **Важно**: Никогда не коммитьте файл `.env` с реальными ключами API в репозиторий!

### Рекомендации по безопасности:

1. Используйте переменные окружения для хранения секретов
2. Ограничьте доступ к API только необходимыми IP адресами
3. Используйте HTTPS в продакшене
4. Регулярно обновляйте зависимости

## Тестирование

### Запуск тестов

```bash
pytest tests/
```

### Ключевые тест-кейсы

- ✅ Генерация подписи для GET запросов
- ✅ Генерация подписи для POST запросов
- ✅ Валидация входных данных
- ✅ Обработка ошибок API
- ✅ Проверка здоровья сервиса

## Масштабирование

### Горизонтальное масштабирование

Для масштабирования приложения рекомендуется:

1. **Load Balancer**: Nginx или HAProxy
2. **Контейнеризация**: Docker + Docker Compose
3. **Оркестрация**: Kubernetes для продакшена
4. **Кэширование**: Redis для временных меток

### Мониторинг

- **Метрики**: Prometheus + Grafana
- **Логи**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Трейсинг**: Jaeger или Zipkin

## Устранение неполадок

### Частые проблемы

1. **"API_SECRET не настроен"**
   - Проверьте файл `.env`
   - Убедитесь, что переменные окружения загружены

2. **"Ошибка запроса к серверу"**
   - Проверьте подключение к интернету
   - Убедитесь, что OKX API доступен

3. **"Неподдерживаемый HTTP метод"**
   - Используйте только: GET, POST, PUT, DELETE

### SSL/TLS ошибки

Если вы получаете ошибки `SSLError` или `Max retries exceeded`, это может быть связано с:

1. **Устаревшими SSL сертификатами** на сервере
2. **Файрволом** или **прокси**, блокирующими HTTPS соединения
3. **Неправильными настройками сети**

#### Решения:

1. **Обновите SSL сертификаты**:
   ```bash
   sudo apt update
   sudo apt install ca-certificates
   sudo update-ca-certificates
   ```

2. **Проверьте файрвол**:
   ```bash
   sudo ufw status
   # Если файрвол активен, разрешите исходящие HTTPS соединения
   sudo ufw allow out 443
   ```

3. **Тестируйте соединение**:
   ```bash
   curl "http://your-server:8000/api/v1/test-connection"
   ```

4. **Запустите диагностический скрипт**:
   ```bash
   python test_ssl.py
   ```

5. **Проверьте DNS**:
   ```bash
   nslookup www.okx.com
   ping www.okx.com
   ```

### Ошибки "socket hang up" / "ECONNRESET"

Если вы получаете ошибки `socket hang up` или `ECONNRESET` при подключении к FastAPI серверу, это может быть связано с:

1. **Неожиданным закрытием соединения** сервером
2. **Проблемами с файрволом** или **прокси**
3. **Таймаутами** на стороне клиента или сервера
4. **Перегрузкой сервера**

#### Диагностика:

1. **Запустите сетевую диагностику**:
   ```bash
   python test_network.py
   ```

2. **Проверьте логи сервера**:
   ```bash
   tail -f logs/app.log
   ```

3. **Проверьте доступность порта**:
   ```bash
   telnet 109.73.192.126 8001
   # или
   nc -zv 109.73.192.126 8001
   ```

4. **Проверьте файрвол на сервере**:
   ```bash
   sudo ufw status
   sudo iptables -L
   ```

#### Решения:

1. **Увеличьте таймауты в n8n**:
   - Установите `timeout: 60000` (60 секунд)
   - Увеличьте `followRedirect: true`

2. **Проверьте настройки сервера**:
   ```bash
   # Перезапустите приложение
   pkill -f "python.*main.py"
   python -m app.main
   ```

3. **Проверьте сетевые настройки**:
   ```bash
   # Проверьте, что порт открыт
   netstat -tlnp | grep 8001
   
   # Проверьте файрвол
   sudo ufw allow 8001
   ```

4. **Мониторинг ресурсов**:
   ```bash
   # Проверьте использование памяти и CPU
   htop
   
   # Проверьте сетевые соединения
   netstat -an | grep 8001
   ```

## Лицензия

MIT License

## Поддержка

При возникновении проблем создайте issue в репозитории или обратитесь к документации OKX API. 