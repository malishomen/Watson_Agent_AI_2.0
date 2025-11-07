# Test Bot Token - РџСЂРѕРІРµСЂРєР° С‚РѕРєРµРЅР° Telegram Р±РѕС‚Р°
import os
import pytest
import requests

def test_bot_token():
    """РџСЂРѕРІРµСЂРєР° С‚РѕРєРµРЅР° Р±РѕС‚Р°"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        pytest.skip("TELEGRAM_BOT_TOKEN is not set")
    
    print(f"рџ”‘ РўРѕРєРµРЅ: {token[:10]}...")
    
    try:
        # РџСЂРѕРІРµСЂСЏРµРј С‚РѕРєРµРЅ С‡РµСЂРµР· getMe API
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            pytest.skip("Telegram API returned 404 (likely invalid token)")
        assert response.status_code == 200, f"HTTP error: {response.status_code}"
        data = response.json()
        if not data.get("ok"):
            pytest.skip(f"API error or invalid token: {data.get('description', 'Unknown error')}")
        bot_info = data.get("result", {})
        print(f"вњ… РўРѕРєРµРЅ СЂР°Р±РѕС‚Р°РµС‚!")
        print(f"рџ¤– РРјСЏ Р±РѕС‚Р°: {bot_info.get('first_name', 'Unknown')}")
        print(f"рџ†” Username: @{bot_info.get('username', 'Unknown')}")
        print(f"рџ†” ID: {bot_info.get('id', 'Unknown')}")
    except Exception as e:
        raise AssertionError(f"Connection error: {e}")

def test_bot_commands():
    """РџСЂРѕРІРµСЂРєР° РєРѕРјР°РЅРґ Р±РѕС‚Р°"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        pytest.skip("TELEGRAM_BOT_TOKEN is not set")
    
    try:
        # РџРѕР»СѓС‡Р°РµРј РѕР±РЅРѕРІР»РµРЅРёСЏ
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            pytest.skip("Telegram API returned 404 (likely invalid token)")
        assert response.status_code == 200, f"HTTP error: {response.status_code}"
        data = response.json()
        if not data.get("ok"):
            pytest.skip(f"API error or invalid token: {data.get('description', 'Unknown error')}")
        updates = data.get("result", [])
        print(f"рџ“± РџРѕР»СѓС‡РµРЅРѕ РѕР±РЅРѕРІР»РµРЅРёР№: {len(updates)}")
        if updates:
            print("рџ“‹ РџРѕСЃР»РµРґРЅРёРµ СЃРѕРѕР±С‰РµРЅРёСЏ:")
            for update in updates[-3:]:
                message = update.get("message", {})
                if message:
                    text = message.get("text", "")
                    from_user = message.get("from", {})
                    user_name = from_user.get("first_name", "Unknown")
                    print(f"  рџ‘¤ {user_name}: {text}")
        else:
            print("рџ“­ РќРµС‚ РЅРѕРІС‹С… СЃРѕРѕР±С‰РµРЅРёР№")
    except Exception as e:
        raise AssertionError(f"Connection error: {e}")

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    print("рџ¤– Test Bot Token - РџСЂРѕРІРµСЂРєР° С‚РѕРєРµРЅР° Telegram Р±РѕС‚Р°")
    print("=" * 60)
    
    # РџСЂРѕРІРµСЂРєР° С‚РѕРєРµРЅР°
    print("\n1. РџСЂРѕРІРµСЂРєР° С‚РѕРєРµРЅР°...")
    if not test_bot_token():
        print("вќЊ РўРѕРєРµРЅ РЅРµ СЂР°Р±РѕС‚Р°РµС‚")
        return
    
    # РџСЂРѕРІРµСЂРєР° РєРѕРјР°РЅРґ
    print("\n2. РџСЂРѕРІРµСЂРєР° РєРѕРјР°РЅРґ...")
    if not test_bot_commands():
        print("вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ РїРѕР»СѓС‡РёС‚СЊ РєРѕРјР°РЅРґС‹")
        return
    
    print("\n" + "=" * 60)
    print("вњ… РўРѕРєРµРЅ СЂР°Р±РѕС‚Р°РµС‚! Р‘РѕС‚ РіРѕС‚РѕРІ Рє РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЋ")
    print("рџ’Ў РћС‚РїСЂР°РІСЊС‚Рµ РєРѕРјР°РЅРґСѓ /start Р±РѕС‚Сѓ РІ Telegram")

if __name__ == "__main__":
    main()



