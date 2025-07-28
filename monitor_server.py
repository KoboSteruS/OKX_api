#!/usr/bin/env python3
"""
Скрипт для мониторинга состояния FastAPI сервера
"""

import requests
import psutil
import time
from datetime import datetime
from loguru import logger

def check_server_health(server_url: str = "http://109.73.192.126:8001"):
    """Проверка здоровья сервера"""
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/health",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds(),
                "data": data
            }
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }

def check_system_resources():
    """Проверка системных ресурсов"""
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "network_connections": len(psutil.net_connections()),
        "processes": len(psutil.pids())
    }

def check_fastapi_process():
    """Проверка процесса FastAPI"""
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'app.main' in cmdline or 'uvicorn' in cmdline:
                return {
                    "found": True,
                    "pid": proc.info['pid'],
                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                    "cpu_percent": proc.cpu_percent(),
                    "status": proc.status()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return {"found": False}

def monitor_server(interval: int = 30):
    """Мониторинг сервера с заданным интервалом"""
    
    print(f"🔍 Запуск мониторинга сервера (интервал: {interval} сек)")
    print("=" * 60)
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📊 Проверка {timestamp}")
        print("-" * 40)
        
        # Проверка здоровья сервера
        health = check_server_health()
        if health["status"] == "healthy":
            print(f"✅ Сервер здоров (ответ: {health['response_time']:.3f}s)")
        else:
            print(f"❌ Проблема с сервером: {health}")
        
        # Проверка системных ресурсов
        resources = check_system_resources()
        print(f"💻 CPU: {resources['cpu_percent']:.1f}%")
        print(f"🧠 RAM: {resources['memory_percent']:.1f}%")
        print(f"💾 Disk: {resources['disk_percent']:.1f}%")
        print(f"🌐 Соединения: {resources['network_connections']}")
        
        # Проверка процесса FastAPI
        process = check_fastapi_process()
        if process["found"]:
            print(f"🔧 FastAPI процесс: PID {process['pid']}")
            print(f"   Память: {process['memory_mb']:.1f} MB")
            print(f"   CPU: {process['cpu_percent']:.1f}%")
            print(f"   Статус: {process['status']}")
        else:
            print("❌ FastAPI процесс не найден!")
        
        # Проверка порта 8001
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 8001))
            sock.close()
            
            if result == 0:
                print("✅ Порт 8001 открыт")
            else:
                print("❌ Порт 8001 закрыт")
        except Exception as e:
            print(f"⚠️ Ошибка проверки порта: {e}")
        
        print("-" * 40)
        print(f"⏰ Следующая проверка через {interval} секунд...")
        
        time.sleep(interval)

if __name__ == "__main__":
    try:
        monitor_server()
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n💥 Ошибка мониторинга: {e}") 