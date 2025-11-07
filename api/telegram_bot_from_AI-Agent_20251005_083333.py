#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot РґР»СЏ AI-Agent
РџРѕР»СѓС‡Р°РµС‚ СЃРѕРѕР±С‰РµРЅРёСЏ Рё РѕС‚РїСЂР°РІР»СЏРµС‚ РёС… РІ /command endpoint
"""
import os
import requests
import time
import json
import urllib.request

# Р—Р°РіСЂСѓР·РєР° РєРѕРЅС„РёРіСѓСЂР°С†РёРё РёР· С„Р°Р№Р»Р°
def load_config():
    """Р—Р°РіСЂСѓР¶Р°РµС‚ РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ РёР· config.env С„Р°Р№Р»Р°"""
    config = {}
    try:
        with open("config.env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print("вљ пёЏ Р¤Р°Р№Р» config.env РЅРµ РЅР°Р№РґРµРЅ, РёСЃРїРѕР»СЊР·СѓРµРј РїРµСЂРµРјРµРЅРЅС‹Рµ РѕРєСЂСѓР¶РµРЅРёСЏ")
    return config

# Р—Р°РіСЂСѓР¶Р°РµРј РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ
config = load_config()

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ
TOKEN = config.get("TG_BOT_TOKEN") or os.getenv("TG_BOT_TOKEN", "")
BASE_URL = config.get("AGENT_API_BASE") or os.getenv("AGENT_API_BASE", "http://127.0.0.1:8088")
SECRET = config.get("AGENT_HTTP_SHARED_SECRET") or os.getenv("AGENT_HTTP_SHARED_SECRET", "")

def tg_api(method: str, **kwargs):
    """Р’С‹Р·РѕРІ API Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    try:
        response = requests.post(url, json=kwargs, timeout=30)
        return response.json()
    except Exception as e:
        print(f"вќЊ Telegram API error: {e}")
        return {"ok": False, "error": str(e)}

def send_to_agent(text: str, session: str = "Telegram") -> str:
    """РћС‚РїСЂР°РІРєР° РєРѕРјР°РЅРґС‹ Р°РіРµРЅС‚Сѓ"""
    try:
        payload = {"text": text, "session": session}
        headers = {
            "x-agent-secret": SECRET,
            "Content-Type": "application/json; charset=utf-8"
        }
        response = requests.post(f"{BASE_URL}/command", 
                               json=payload, 
                               headers=headers, 
                               timeout=30)
        result = response.json()
        
        if result.get("ok"):
            return f"в†’ {result.get('normalized', '')}\n\n{result.get('result', '')}"
        else:
            return f"вќЊ РћС€РёР±РєР°: {result.get('result', 'unknown')}"
    except Exception as e:
        return f"вќЊ РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ: {e}"

def get_pending_approvals() -> list:
    """РџРѕР»СѓС‡РµРЅРёРµ СЃРїРёСЃРєР° РѕР¶РёРґР°СЋС‰РёС… РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ Р·Р°СЏРІРѕРє"""
    try:
        headers = {
            "x-agent-secret": SECRET,
            "Content-Type": "application/json; charset=utf-8"
        }
        response = requests.get(f"{BASE_URL}/approvals/pending", 
                               headers=headers, 
                               timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ pending approvals: {e}")
        return []

def format_pending_approvals() -> str:
    """Р¤РѕСЂРјР°С‚РёСЂРѕРІР°РЅРёРµ СЃРїРёСЃРєР° pending approvals РґР»СЏ РѕС‚РїСЂР°РІРєРё РІ Telegram"""
    approvals = get_pending_approvals()
    if not approvals:
        return "вњ… РќРµС‚ РѕР¶РёРґР°СЋС‰РёС… РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ Р·Р°СЏРІРѕРє"

    msg = f"вЏі РћР¶РёРґР°СЋС‚ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ ({len(approvals)} Р·Р°СЏРІРѕРє):\n\n"
    for approval in approvals[:5]:  # РїРѕРєР°Р·С‹РІР°РµРј С‚РѕР»СЊРєРѕ РїРµСЂРІС‹Рµ 5
        msg += f"рџ†” {approval['id']}\n"
        msg += f"рџ“ќ {approval['action']}\n"
        msg += f"вЏ° {approval['created_at']}\n"
        msg += f"вњ… /approve {approval['id']}\n\n"

    if len(approvals) > 5:
        msg += f"... Рё РµС‰Рµ {len(approvals) - 5} Р·Р°СЏРІРѕРє"

    return msg

def handle_message(chat_id: int, text: str):
    """РћР±СЂР°Р±РѕС‚РєР° СЃРѕРѕР±С‰РµРЅРёСЏ РѕС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    print(f"рџ“Ё РџРѕР»СѓС‡РµРЅРѕ СЃРѕРѕР±С‰РµРЅРёРµ РѕС‚ {chat_id}: {text}")
    
    # РЎРїРµС†РёР°Р»СЊРЅС‹Рµ РєРѕРјР°РЅРґС‹
    if text == "/ping":
        response = "рџЏ“ Pong! Р‘РѕС‚ СЂР°Р±РѕС‚Р°РµС‚"
    elif text == "/status":
        response = "вњ… AI-Agent API СЂР°Р±РѕС‚Р°РµС‚\n" + format_pending_approvals()
    elif text.startswith("/approve "):
        approval_id = text.split(" ", 1)[1]
        # РћС‚РїСЂР°РІР»СЏРµРј РєРѕРјР°РЅРґСѓ approve Р°РіРµРЅС‚Сѓ
        response = send_to_agent(f"/approve {approval_id}", f"TG-{chat_id}")
    else:
        # РћР±С‹С‡РЅРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ - РѕС‚РїСЂР°РІР»СЏРµРј Р°РіРµРЅС‚Сѓ
        response = send_to_agent(text, f"TG-{chat_id}")
    
    # РћС‚РїСЂР°РІР»СЏРµРј РѕС‚РІРµС‚
    result = tg_api("sendMessage", 
                   chat_id=chat_id, 
                   text=response[:4000])  # Telegram Р»РёРјРёС‚ 4096 СЃРёРјРІРѕР»РѕРІ
    
    if result.get("ok"):
        print(f"вњ… РћС‚РІРµС‚ РѕС‚РїСЂР°РІР»РµРЅ РІ {chat_id}")
    else:
        print(f"вќЊ РћС€РёР±РєР° РѕС‚РїСЂР°РІРєРё: {result}")

def main():
    """РћСЃРЅРѕРІРЅРѕР№ С†РёРєР» Р±РѕС‚Р°"""
    print("рџ¤– Р—Р°РїСѓСЃРє Telegram Р±РѕС‚Р°...")
    
    # РџСЂРѕРІРµСЂСЏРµРј С‚РѕРєРµРЅ
    if not TOKEN:
        print("вќЊ TG_BOT_TOKEN РЅРµ СѓСЃС‚Р°РЅРѕРІР»РµРЅ!")
        return
    
    # РџСЂРѕРІРµСЂСЏРµРј API Р°РіРµРЅС‚Р°
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"вќЊ AI-Agent API РЅРµРґРѕСЃС‚СѓРїРµРЅ: {response.status_code}")
            return
    except Exception as e:
        print(f"вќЊ РќРµ СѓРґР°РµС‚СЃСЏ РїРѕРґРєР»СЋС‡РёС‚СЊСЃСЏ Рє AI-Agent API: {e}")
        return
    
    print("вњ… AI-Agent API РґРѕСЃС‚СѓРїРµРЅ")
    
    # РџСЂРѕРІРµСЂСЏРµРј С‚РѕРєРµРЅ Р±РѕС‚Р°
    me = tg_api("getMe")
    if not me.get("ok"):
        print(f"вќЊ РќРµРІРµСЂРЅС‹Р№ С‚РѕРєРµРЅ Р±РѕС‚Р°: {me}")
        return
    
    print(f"вњ… Р‘РѕС‚ @{me['result']['username']} РіРѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ")
    
    # РЎР±СЂР°СЃС‹РІР°РµРј webhook (РёСЃРїРѕР»СЊР·СѓРµРј polling)
    tg_api("deleteWebhook")
    print("вњ… Webhook СЃР±СЂРѕС€РµРЅ, РёСЃРїРѕР»СЊР·СѓРµРј polling")
    
    offset = None
    
    print("рџ”„ РќР°С‡РёРЅР°РµРј polling...")
    while True:
        try:
            # РџРѕР»СѓС‡Р°РµРј РѕР±РЅРѕРІР»РµРЅРёСЏ
            updates = tg_api("getUpdates", 
                           timeout=30, 
                           offset=offset)
            
            if not updates.get("ok"):
                print(f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ updates: {updates}")
                time.sleep(5)
                continue
            
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    if text:
                        handle_message(chat_id, text)
            
            time.sleep(0.5)  # РќРµР±РѕР»СЊС€Р°СЏ РїР°СѓР·Р° РјРµР¶РґСѓ Р·Р°РїСЂРѕСЃР°РјРё
            
        except KeyboardInterrupt:
            print("\nрџ›‘ РћСЃС‚Р°РЅРѕРІРєР° Р±РѕС‚Р°...")
            break
        except Exception as e:
            print(f"вќЊ РћС€РёР±РєР° РІ РѕСЃРЅРѕРІРЅРѕРј С†РёРєР»Рµ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
