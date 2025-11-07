# Test Bot Token - Проверка токена Telegram бота
import os
import requests

def test_bot_token():
    """Проверка токена бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Токен не установлен")
        return False
    
    print(f"🔑 Токен: {token[:10]}...")
    
    try:
        # Проверяем токен через getMe API
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Токен работает!")
                print(f"🤖 Имя бота: {bot_info.get('first_name', 'Unknown')}")
                print(f"🆔 Username: @{bot_info.get('username', 'Unknown')}")
                print(f"🆔 ID: {bot_info.get('id', 'Unknown')}")
                return True
            else:
                print(f"❌ Ошибка API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {str(e)}")
        return False

def test_bot_commands():
    """Проверка команд бота"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Токен не установлен")
        return False
    
    try:
        # Получаем обновления
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                updates = data.get("result", [])
                print(f"📱 Получено обновлений: {len(updates)}")
                
                if updates:
                    print("📋 Последние сообщения:")
                    for update in updates[-3:]:  # Последние 3
                        message = update.get("message", {})
                        if message:
                            text = message.get("text", "")
                            from_user = message.get("from", {})
                            user_name = from_user.get("first_name", "Unknown")
                            print(f"  👤 {user_name}: {text}")
                else:
                    print("📭 Нет новых сообщений")
                
                return True
            else:
                print(f"❌ Ошибка API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {str(e)}")
        return False

def main():
    """Главная функция"""
    print("🤖 Test Bot Token - Проверка токена Telegram бота")
    print("=" * 60)
    
    # Проверка токена
    print("\n1. Проверка токена...")
    if not test_bot_token():
        print("❌ Токен не работает")
        return
    
    # Проверка команд
    print("\n2. Проверка команд...")
    if not test_bot_commands():
        print("❌ Не удалось получить команды")
        return
    
    print("\n" + "=" * 60)
    print("✅ Токен работает! Бот готов к использованию")
    print("💡 Отправьте команду /start боту в Telegram")

if __name__ == "__main__":
    main()


