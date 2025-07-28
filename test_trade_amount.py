#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой функциональности торговой стратегии
с передачей суммы покупки BTC
"""

import requests
import json

# URL вашего API
BASE_URL = "http://localhost:8000"

def test_trade_strategy_with_amount():
    """Тест торговой стратегии с указанием суммы покупки"""
    
    print("=== Тест торговой стратегии с суммой покупки ===")
    
    # Тест POST запроса
    print("\n1. Тест POST /trade с суммой покупки:")
    post_data = {
        "wait_minutes": 1,  # Короткое время для теста
        "buy_amount": 5.0   # Сумма в USDT
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/trade",
            json=post_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Ответ:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Ошибка: {response.text}")
            
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    
    # Тест GET запроса
    print("\n2. Тест GET /trade с суммой покупки:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/trade",
            params={
                "wait_minutes": 1,
                "buy_amount": 3.0
            }
        )
        
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Ответ:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Ошибка: {response.text}")
            
    except Exception as e:
        print(f"Ошибка запроса: {e}")

def test_schema_validation():
    """Тест валидации схемы"""
    
    print("\n=== Тест валидации схемы ===")
    
    # Тест с некорректной суммой (отрицательной)
    print("\n1. Тест с отрицательной суммой:")
    post_data = {
        "wait_minutes": 5,
        "buy_amount": -5.0  # Некорректная сумма
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/trade",
            json=post_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        
    except Exception as e:
        print(f"Ошибка запроса: {e}")

if __name__ == "__main__":
    print("Запуск тестов торговой стратегии с суммой покупки...")
    
    # Проверяем, что сервер запущен
    try:
        health_response = requests.get(f"{BASE_URL}/api/v1/health")
        if health_response.status_code == 200:
            print("✅ Сервер доступен")
            test_trade_strategy_with_amount()
            test_schema_validation()
        else:
            print("❌ Сервер недоступен")
    except Exception as e:
        print(f"❌ Не удается подключиться к серверу: {e}")
        print("Убедитесь, что сервер запущен командой:")
        print("python -m app.main")
        print("или")
        print("uvicorn app.main:app --host 0.0.0.0 --port 8000") 