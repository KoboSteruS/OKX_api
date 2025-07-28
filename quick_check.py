#!/usr/bin/env python3
"""
Быстрая проверка состояния FastAPI сервера
"""

import requests
import socket
import subprocess
import sys
from datetime import datetime

def quick_server_check():
    """Быстрая проверка сервера"""
    
    server_url = "http://109.73.192.126:8001"
    
    print("🔍 Быстрая проверка сервера")
    print("=" * 40)
    print(f"Время: {datetime.now()}")
    print(f"Сервер: {server_url}")
    print("-" * 40)
    
    # Проверка 1: Доступность порта
    print("1. Проверка порта 8001...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('109.73.192.126', 8001))
        sock.close()
        
        if result == 0:
            print("   ✅ Порт 8001 открыт")
        else:
            print("   ❌ Порт 8001 закрыт")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка проверки порта: {e}")
        return False
    
    # Проверка 2: HTTP ответ
    print("2. Проверка HTTP ответа...")
    try:
        response = requests.get(
            f"{server_url}/api/v1/health",
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ HTTP ответ успешен")
            print(f"   Время ответа: {response.elapsed.total_seconds():.3f}s")
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка HTTP: {e}")
        return False
    
    # Проверка 3: Процесс FastAPI
    print("3. Проверка процесса FastAPI...")
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'app.main'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"   ✅ Найдено процессов: {len(pids)}")
            for pid in pids:
                if pid:
                    print(f"      PID: {pid}")
        else:
            print("   ❌ Процесс FastAPI не найден")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Не удалось проверить процесс: {e}")
    
    # Проверка 4: Системные ресурсы
    print("4. Проверка системных ресурсов...")
    try:
        # CPU
        cpu_result = subprocess.run(
            ['top', '-bn1', '|', 'grep', '"Cpu(s)"'],
            shell=True, capture_output=True, text=True
        )
        if cpu_result.stdout:
            print(f"   CPU: {cpu_result.stdout.strip()}")
        
        # Память
        mem_result = subprocess.run(
            ['free', '-h'],
            capture_output=True, text=True
        )
        if mem_result.stdout:
            lines = mem_result.stdout.strip().split('\n')
            if len(lines) > 1:
                mem_line = lines[1]
                print(f"   RAM: {mem_line}")
                
    except Exception as e:
        print(f"   ⚠️ Не удалось проверить ресурсы: {e}")
    
    print("-" * 40)
    print("✅ Сервер работает нормально")
    return True

if __name__ == "__main__":
    if quick_server_check():
        print("\n🎉 Все проверки пройдены!")
        sys.exit(0)
    else:
        print("\n💥 Обнаружены проблемы!")
        print("\nРекомендации:")
        print("1. Перезапустите сервер: pkill -f 'python.*main.py' && python -m app.main")
        print("2. Проверьте логи: tail -f logs/app.log")
        print("3. Запустите полную диагностику: python test_network.py")
        sys.exit(1) 