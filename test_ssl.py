#!/usr/bin/env python3
"""
Скрипт для тестирования SSL соединения с OKX API
"""

import requests
import ssl
import socket
from datetime import datetime

def test_ssl_connection():
    """Тестирование SSL соединения с OKX API"""
    
    print("🔍 Тестирование SSL соединения с OKX API...")
    print("=" * 50)
    
    # Тест 1: Проверка DNS
    print("1. Проверка DNS...")
    try:
        ip = socket.gethostbyname('www.okx.com')
        print(f"✅ DNS резолвинг: www.okx.com -> {ip}")
    except socket.gaierror as e:
        print(f"❌ Ошибка DNS: {e}")
        return False
    
    # Тест 2: Проверка SSL сертификата
    print("\n2. Проверка SSL сертификата...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(('www.okx.com', 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='www.okx.com') as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL сертификат валиден")
                print(f"   Сертификат выдан для: {cert.get('subject', [])}")
                print(f"   Действителен до: {cert.get('notAfter', 'Unknown')}")
    except Exception as e:
        print(f"❌ Ошибка SSL: {e}")
        return False
    
    # Тест 3: HTTP запрос
    print("\n3. Тестирование HTTP запроса...")
    try:
        response = requests.get(
            'https://www.okx.com/api/v5/public/time',
            timeout=10,
            verify=True
        )
        if response.status_code == 200:
            print("✅ HTTP запрос успешен")
            data = response.json()
            print(f"   Время сервера OKX: {data.get('data', [{}])[0].get('ts', 'Unknown')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL ошибка при HTTP запросе: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Все тесты пройдены успешно!")
    print("Соединение с OKX API работает корректно.")
    return True

def check_system_info():
    """Проверка системной информации"""
    print("\n📋 Системная информация:")
    print("=" * 30)
    
    import platform
    print(f"ОС: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Requests: {requests.__version__}")
    
    # Проверка SSL версии
    try:
        print(f"SSL: {ssl.OPENSSL_VERSION}")
    except:
        print("SSL: Версия недоступна")

if __name__ == "__main__":
    print("🚀 Запуск диагностики SSL соединения")
    print(f"Время: {datetime.now()}")
    
    check_system_info()
    
    if test_ssl_connection():
        print("\n🎉 Диагностика завершена успешно!")
    else:
        print("\n💥 Обнаружены проблемы с соединением!")
        print("\nРекомендации:")
        print("1. Обновите SSL сертификаты: sudo apt update && sudo apt install ca-certificates")
        print("2. Проверьте файрвол: sudo ufw status")
        print("3. Проверьте DNS: nslookup www.okx.com")
        print("4. Перезапустите приложение после исправления") 