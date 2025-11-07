# Simple Test Bot - РџСЂРѕСЃС‚РѕР№ С‚РµСЃС‚РѕРІС‹Р№ Р±РѕС‚ Р±РµР· Telegram
# РџСЂРѕРІРµСЂРєР° СЂР°Р±РѕС‚С‹ API Р°РіРµРЅС‚Р° Рё СЃРѕР·РґР°РЅРёСЏ Р·Р°РґР°С‡

import requests
import json
import time
import os

def test_api_health():
    """РџСЂРѕРІРµСЂРєР° Р·РґРѕСЂРѕРІСЊСЏ API"""
    try:
        response = requests.get("http://127.0.0.1:8088/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"вњ… API Agent: {data['status']}")
            print(f"вњ… LM Studio: {'Р Р°Р±РѕС‚Р°РµС‚' if data['lm_studio'] else 'РќРµ СЂР°Р±РѕС‚Р°РµС‚'}")
            print(f"вњ… Cursor: {'Р”РѕСЃС‚СѓРїРµРЅ' if data['cursor_available'] else 'РќРµ РґРѕСЃС‚СѓРїРµРЅ'}")
            return True
        else:
            print(f"вќЊ API Agent: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"вќЊ API Agent: {str(e)}")
        return False

def create_task(task_description):
    """РЎРѕР·РґР°РЅРёРµ Р·Р°РґР°С‡Рё"""
    try:
        task_data = {
            "task": task_description,
            "project_path": "D:\\AI-Agent\\Memory",
            "timeout": 300
        }
        
        response = requests.post("http://127.0.0.1:8088/task", json=task_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"вњ… Р—Р°РґР°С‡Р° СЃРѕР·РґР°РЅР°: {data['task_id']}")
            print(f"рџ“ќ РћРїРёСЃР°РЅРёРµ: {task_description}")
            return data['task_id']
        else:
            print(f"вќЊ РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ Р·Р°РґР°С‡Рё: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ Р·Р°РґР°С‡Рё: {str(e)}")
        return None

def simulate_bot_interaction():
    """РЎРёРјСѓР»СЏС†РёСЏ СЂР°Р±РѕС‚С‹ Р±РѕС‚Р°"""
    print("рџ¤– РЎРёРјСѓР»СЏС†РёСЏ Telegram Р±РѕС‚Р°")
    print("=" * 50)
    
    # РџСЂРѕРІРµСЂРєР° API
    if not test_api_health():
        print("вќЊ API Р°РіРµРЅС‚ РЅРµ СЂР°Р±РѕС‚Р°РµС‚. Р—Р°РїСѓСЃС‚РёС‚Рµ: python -m uvicorn api.agent:app --host 127.0.0.1 --port 8088")
        return
    
    # РЎРїРёСЃРѕРє С‚РµСЃС‚РѕРІС‹С… Р·Р°РґР°С‡
    test_tasks = [
        "РЎРѕР·РґР°С‚СЊ РїСЂРѕСЃС‚РѕРµ РІРµР±-РїСЂРёР»РѕР¶РµРЅРёРµ РЅР° FastAPI",
        "Р”РѕР±Р°РІРёС‚СЊ Р°СѓС‚РµРЅС‚РёС„РёРєР°С†РёСЋ РІ РїСЂРѕРµРєС‚",
        "РЎРѕР·РґР°С‚СЊ REST API РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏРјРё",
        "РќР°СЃС‚СЂРѕРёС‚СЊ Р±Р°Р·Сѓ РґР°РЅРЅС‹С… PostgreSQL",
        "РЎРѕР·РґР°С‚СЊ С„СЂРѕРЅС‚РµРЅРґ РЅР° React"
    ]
    
    print(f"\nрџ“‹ РўРµСЃС‚РѕРІС‹Рµ Р·Р°РґР°С‡Рё:")
    for i, task in enumerate(test_tasks, 1):
        print(f"{i}. {task}")
    
    print(f"\nрџљЂ РЎРѕР·РґР°РЅРёРµ Р·Р°РґР°С‡...")
    
    created_tasks = []
    for i, task in enumerate(test_tasks, 1):
        print(f"\n--- Р—Р°РґР°С‡Р° {i} ---")
        task_id = create_task(task)
        if task_id:
            created_tasks.append(task_id)
        time.sleep(1)  # РџР°СѓР·Р° РјРµР¶РґСѓ Р·Р°РґР°С‡Р°РјРё
    
    print(f"\n" + "=" * 50)
    print(f"рџ“Љ Р РµР·СѓР»СЊС‚Р°С‚:")
    print(f"вњ… РЎРѕР·РґР°РЅРѕ Р·Р°РґР°С‡: {len(created_tasks)}")
    print(f"рџ“ќ ID Р·Р°РґР°С‡: {', '.join(created_tasks)}")
    
    if created_tasks:
        print(f"\nрџЋЇ Р—Р°РґР°С‡Рё РѕС‚РїСЂР°РІР»РµРЅС‹ РІ Cursor РґР»СЏ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРіРѕ РІС‹РїРѕР»РЅРµРЅРёСЏ!")
        print(f"рџ’Ў РџСЂРѕРІРµСЂСЊС‚Рµ Cursor - С‚Р°Рј РґРѕР»Р¶РЅС‹ РїРѕСЏРІРёС‚СЊСЃСЏ РЅРѕРІС‹Рµ С„Р°Р№Р»С‹ Рё РєРѕРґ")
    else:
        print(f"\nвќЊ РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Рё")

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    print("рџ¤– Simple Test Bot - РЎРёРјСѓР»СЏС†РёСЏ Telegram Р±РѕС‚Р°")
    print("=" * 60)
    
    # РЎРёРјСѓР»СЏС†РёСЏ СЂР°Р±РѕС‚С‹ Р±РѕС‚Р°
    simulate_bot_interaction()
    
    print(f"\n" + "=" * 60)
    print(f"рџ’Ў Р”Р»СЏ РЅР°СЃС‚СЂРѕР№РєРё РЅР°СЃС‚РѕСЏС‰РµРіРѕ Telegram Р±РѕС‚Р°:")
    print(f"1. РЎРѕР·РґР°Р№С‚Рµ Р±РѕС‚Р° С‡РµСЂРµР· @BotFather РІ Telegram")
    print(f"2. РЈСЃС‚Р°РЅРѕРІРёС‚Рµ С‚РѕРєРµРЅ: $env:TELEGRAM_BOT_TOKEN = 'your_token'")
    print(f"3. Р—Р°РїСѓСЃС‚РёС‚Рµ: python telegram_bot.py")

if __name__ == "__main__":
    main()


