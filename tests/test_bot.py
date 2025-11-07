# Test Bot - Простой тестовый бот для проверки
# Минимальная версия для тестирования

import os
import requests
import pytest
import json

@pytest.mark.integration
def test_api_connection():
    """Тест подключения к API"""
    try:
        response = requests.get("http://127.0.0.1:8088/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Agent: {data['status']}")
            print(f"✅ LM Studio: {'Работает' if data['lm_studio'] else 'Не работает'}")
            print(f"✅ Cursor: {'Доступен' if data['cursor_available'] else 'Не доступен'}")
            return True
        else:
            print(f"❌ API Agent: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Agent: {str(e)}")
        return False

@pytest.mark.integration
def test_task_creation():
    """Тест создания задачи"""
    try:
        task_data = {
            "task": "Test task from bot",
            "project_path": "D:\\AI-Agent\\Memory",
            "timeout": 300
        }
        
        response = requests.post("http://127.0.0.1:8088/task", json=task_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task created: {data['task_id']}")
            return True
        else:
            print(f"❌ Task creation failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Task creation error: {str(e)}")
        return False

def main():
    """Главная функция тестирования"""
    print("🤖 Testing Telegram Bot Integration")
    print("=" * 50)
    
    # Тест 1: Подключение к API
    print("\n1. Testing API connection...")
    api_ok = test_api_connection()
    
    # Тест 2: Создание задачи
    print("\n2. Testing task creation...")
    task_ok = test_task_creation()
    
    # Результат
    print("\n" + "=" * 50)
    if api_ok and task_ok:
        print("✅ All tests passed! Bot integration is ready.")
        print("\n🚀 To start the bot:")
        print("1. Set bot token: $env:TELEGRAM_BOT_TOKEN = 'your_token'")
        print("2. Run: python telegram_bot.py")
    else:
        print("❌ Some tests failed. Check the issues above.")
        
        if not api_ok:
            print("\n🔧 Fix API Agent:")
            print("python -m uvicorn api.agent:app --host 127.0.0.1 --port 8088")

if __name__ == "__main__":
    main()


