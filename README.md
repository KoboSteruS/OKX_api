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

### 1. Выполнение торговой стратегии (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/trade" \
  -H "Content-Type: application/json" \
  -d '{"wait_minutes": 5, "buy_amount": 10.0}'
```

### 2. Выполнение торговой стратегии (GET)

```bash
curl "http://localhost:8000/api/v1/trade?wait_minutes=3&buy_amount=15.0"
```

### 3. Получение комплексных рыночных данных (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/market-data" \
  -H "Content-Type: application/json" \
  -d '{"inst_id": "BTC-USDT"}'
```

### 4. Получение упрощенных рыночных данных (GET)

```bash
curl "http://localhost:8000/api/v1/market-data?inst_id=BTC-USDT"
```

**Включает**: тикер, стакан ордеров (3 уровня), последние 10 свечей

### 5. Получение данных всех тикеров (POST)

```bash
curl -X POST "http://localhost:8000/api/v1/tickers" \
  -H "Content-Type: application/json" \
  -d '{"inst_type": "SPOT"}'
```

### 6. Получение данных всех тикеров (GET)

```bash
curl "http://localhost:8000/api/v1/tickers?inst_type=SWAP"
```

### 7. Получение информации о валютах

```bash
curl "http://localhost:8000/api/v1/currencies"
```

### 8. Проверка здоровья сервиса

```bash
curl "http://localhost:8000/api/v1/health"
```

## ⚠️ Важно: Торговая стратегия

Приложение выполняет **автоматическую торговую стратегию** в демо-режиме:

1. **Покупка**: BTC на указанную сумму USDT (по умолчанию 10.0 USDT)
2. **Ожидание**: Указанное количество минут
3. **Продажа**: Весь доступный BTC

**Демо-режим**: Все операции выполняются в симуляционном режиме (`x-simulated-trading: 1`)

**Параметры**:
- `wait_minutes`: Время ожидания в минутах (1-60, по умолчанию 5)
- `buy_amount`: Сумма в USDT для покупки BTC (больше 0, по умолчанию 10.0)

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

## Лицензия

MIT License

## Поддержка

При возникновении проблем создайте issue в репозитории или обратитесь к документации OKX API. 