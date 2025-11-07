#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
РЈРїСЂРѕС‰РµРЅРЅС‹Р№ Telegram Р±РѕС‚ РґР»СЏ Windows
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# РќР°СЃС‚СЂР°РёРІР°РµРј Р»РѕРіРёСЂРѕРІР°РЅРёРµ
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("simple_bot")

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ
BOT_TOKEN = "7073794782:AAHgCryXTUXZ0TOvQ7_xZaccTBp_uwm0gvk"
ALLOWED_USERS = ["73332538"]
ADMIN_USER = "73332538"
AGENT_SCRIPT = str(Path(__file__).parent / "Memory" / "GPT+Deepseek_Agent_memory.py")

def call_agent(command):
    """Р’С‹Р·РѕРІ Р°РіРµРЅС‚Р° С‡РµСЂРµР· subprocess"""
    try:
        cmd = ["python", AGENT_SCRIPT, "--session", "Danil-PC", "--once", command]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() or result.stderr.strip() or "(РїСѓСЃС‚Рѕ)"
    except Exception as e:
        return f"РћС€РёР±РєР°: {e}"

def process_command(user_id, text):
    """РћР±СЂР°Р±РѕС‚РєР° РєРѕРјР°РЅРґС‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ"""
    if str(user_id) not in ALLOWED_USERS:
        return "Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ."
    
    text = text.strip()
    
    if text == "/start":
        return "Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ! РљРѕРјР°РЅРґС‹: /pwd, /cmd <РєРѕРјР°РЅРґР°>, /notes, /remember <С‚РµРєСЃС‚>"
    
    elif text == "/pwd":
        return call_agent("/pwd")
    
    elif text == "/notes":
        return call_agent("/notes")
    
    elif text.startswith("/cmd "):
        command = text[5:].strip()
        return call_agent(command)
    
    elif text.startswith("/remember "):
        note = text[10:].strip()
        return call_agent(f"/remember {note}")
    
    elif text.startswith("/approve "):
        if str(user_id) != ADMIN_USER:
            return "РўРѕР»СЊРєРѕ Р°РґРјРёРЅ РјРѕР¶РµС‚ РїРѕРґС‚РІРµСЂР¶РґР°С‚СЊ."
        approval_id = text[9:].strip()
        return call_agent(f"/approve {approval_id}")
    
    else:
        # РћР±С‹С‡РЅС‹Р№ С‚РµРєСЃС‚ - РїРµСЂРµРґР°РµРј Р°РіРµРЅС‚Сѓ
        return call_agent(text)

def send_message(chat_id, text):
    """РћС‚РїСЂР°РІРєР° СЃРѕРѕР±С‰РµРЅРёСЏ С‡РµСЂРµР· Telegram API"""
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text[:4000],  # РћРіСЂР°РЅРёС‡РµРЅРёРµ Telegram
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        log.error(f"РћС€РёР±РєР° РѕС‚РїСЂР°РІРєРё: {e}")
        return None

def main():
    """РћСЃРЅРѕРІРЅРѕР№ С†РёРєР» Р±РѕС‚Р°"""
    log.info("Р—Р°РїСѓСЃРє РїСЂРѕСЃС‚РѕРіРѕ Telegram Р±РѕС‚Р°...")
    
    offset = 0
    
    while True:
        try:
            import requests
            
            # РџРѕР»СѓС‡Р°РµРј РѕР±РЅРѕРІР»РµРЅРёСЏ
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if not data.get("ok"):
                log.error(f"API РѕС€РёР±РєР°: {data}")
                continue
            
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                
                if "message" in update:
                    message = update["message"]
                    user_id = message["from"]["id"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    log.info(f"РЎРѕРѕР±С‰РµРЅРёРµ РѕС‚ {user_id}: {text}")
                    
                    # РћР±СЂР°Р±Р°С‚С‹РІР°РµРј РєРѕРјР°РЅРґСѓ
                    response_text = process_command(user_id, text)
                    
                    # РћС‚РїСЂР°РІР»СЏРµРј РѕС‚РІРµС‚
                    send_message(chat_id, response_text)
                    
        except KeyboardInterrupt:
            log.info("Р‘РѕС‚ РѕСЃС‚Р°РЅРѕРІР»РµРЅ")
            break
        except Exception as e:
            log.error(f"РћС€РёР±РєР°: {e}")
            continue

if __name__ == "__main__":
    main()
