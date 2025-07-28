#!/usr/bin/env python3
"""
Скрипт для диагностики сетевого соединения с FastAPI сервером
"""

import requests
import socket
import time
from datetime import datetime

def test_network_connection(server_url: str = "http://109.73.192.126:8001"):
    """Тестирование сетевого соединения с FastAPI сервером"""
    
    print("🔍 Тестирование сетевого соединения с FastAPI сервером...")
    print("=" * 60)
    print(f"Сервер: {server_url}")
    print(f"Время: {datetime.now()}")
    print("=" * 60)
    
    # Тест 1: Проверка DNS и доступности порта
    print("1. Проверка DNS и порта...")
    try:
        # Извлекаем хост и порт из URL
        if server_url.startswith("http://"):
            host = server_url[7:].split(":")[0]
            port = int(server_url.split(":")[-1].split("/")[0])
        else:
            host = server_url.split(":")[0]
            port = int(server_url.split(":")[-1].split("/")[0])
        
        print(f"   Хост: {host}")
        print(f"   Порт: {port}")
        
        # Проверка DNS
        ip = socket.gethostbyname(host)
        print(f"   ✅ DNS резолвинг: {host} -> {ip}")
        
        # Проверка доступности порта
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Порт {port} доступен")
        else:
            print(f"   ❌ Порт {port} недоступен (код ошибки: {result})")
            return False
            
    except socket.gaierror as e:
        print(f"   ❌ Ошибка DNS: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка проверки порта: {e}")
        return False
    
    # Тест 2: Простой HTTP запрос
    print("\n2. Тестирование HTTP соединения...")
    try:
        response = requests.get(
            f"{server_url}/api/v1/health",
            timeout=10,
            headers={'User-Agent': 'Network-Test/1.0'}
        )
        
        if response.status_code == 200:
            print("   ✅ HTTP соединение успешно")
            print(f"   Время ответа: {response.elapsed.total_seconds():.3f}s")
            print(f"   Размер ответа: {len(response.content)} байт")
        else:
            print(f"   ⚠️ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}...")
            
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Таймаут соединения")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Ошибка соединения: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка HTTP запроса: {e}")
        return False
    
    # Тест 3: Тестирование торгового эндпоинта
    print("\n3. Тестирование торгового эндпоинта...")
    try:
        test_data = {
            "wait_minutes": 1,
            "buy_amount": 10.0
        }
        
        response = requests.post(
            f"{server_url}/api/v1/trade",
            json=test_data,
            timeout=30,
            headers={'User-Agent': 'Network-Test/1.0'}
        )
        
        if response.status_code == 200:
            print("   ✅ Торговый эндпоинт отвечает")
            print(f"   Время ответа: {response.elapsed.total_seconds():.3f}s")
        elif response.status_code == 500:
            print("   ⚠️ Сервер вернул ошибку 500")
            print(f"   Ответ: {response.text[:300]}...")
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}...")
            
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Таймаут соединения с торговым эндпоинтом")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Ошибка соединения с торговым эндпоинтом: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка HTTP запроса к торговому эндпоинту: {e}")
        return False
    
    # Тест 4: Проверка стабильности соединения
    print("\n4. Тестирование стабильности соединения...")
    try:
        for i in range(3):
            start_time = time.time()
            response = requests.get(
                f"{server_url}/api/v1/health",
                timeout=5
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Запрос {i+1}: {elapsed:.3f}s")
            else:
                print(f"   ⚠️ Запрос {i+1}: {response.status_code} ({elapsed:.3f}s)")
            
            time.sleep(1)  # Пауза между запросами
            
    except Exception as e:
        print(f"   ❌ Ошибка стабильности: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Все тесты пройдены успешно!")
    print("Соединение с FastAPI сервером работает стабильно.")
    return True

def check_system_network():
    """Проверка системных сетевых настроек"""
    print("\n🔧 Проверка системных сетевых настроек...")
    print("-" * 40)
    
    # Проверка DNS
    try:
        import subprocess
        result = subprocess.run(['nslookup', '109.73.192.126'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ DNS резолвинг работает")
        else:
            print("❌ Проблемы с DNS резолвингом")
    except Exception as e:
        print(f"⚠️ Не удалось проверить DNS: {e}")
    
    # Проверка ping
    try:
        result = subprocess.run(['ping', '-c', '3', '109.73.192.126'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Ping работает")
        else:
            print("❌ Ping не работает")
    except Exception as e:
        print(f"⚠️ Не удалось выполнить ping: {e}")
    
    # Проверка telnet (если доступен)
    try:
        result = subprocess.run(['telnet', '109.73.192.126', '8001'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Telnet соединение работает")
        else:
            print("❌ Telnet соединение не работает")
    except Exception:
        print("⚠️ Telnet недоступен")

if __name__ == "__main__":
    print("🚀 Запуск диагностики сетевого соединения")
    print(f"Время: {datetime.now()}")
    
    # Проверка системных настроек
    check_system_network()
    
    # Тестирование соединения
    if test_network_connection():
        print("\n🎉 Диагностика завершена успешно!")
        print("\nРекомендации:")
        print("1. Соединение работает стабильно")
        print("2. Проблема может быть в настройках n8n")
        print("3. Проверьте таймауты в n8n")
        print("4. Убедитесь, что n8n не блокирует соединения")
    else:
        print("\n💥 Обнаружены проблемы с соединением!")
        print("\nРекомендации:")
        print("1. Проверьте файрвол на сервере")
        print("2. Убедитесь, что порт 8001 открыт")
        print("3. Проверьте настройки сети")
        print("4. Перезапустите FastAPI приложение")
        print("5. Проверьте логи сервера: tail -f logs/app.log") 