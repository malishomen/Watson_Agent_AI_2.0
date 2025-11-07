#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import os

API_URL = "http://127.0.0.1:8088/command"
SECRET = os.getenv("AGENT_HTTP_SHARED_SECRET", "")

def send_to_agent(text: str, session: str = "Telegram") -> str:
    """
    РћС‚РїСЂР°РІР»СЏРµС‚ РєРѕРјР°РЅРґСѓ Р°РіРµРЅС‚Сѓ С‡РµСЂРµР· FastAPI endpoint /command
    """
    try:
        r = requests.post(API_URL,
            json={"text": text, "session": session},
            headers={
                "x-agent-secret": SECRET, 
                "Content-Type": "application/json; charset=utf-8"
            },
            timeout=30
        )
        j = r.json()
        if j.get("ok"):
            return f"в†’ {j['normalized']}\n\n{j['result']}"
        return f"РћС€РёР±РєР°: {j.get('result','unknown')}"
    except Exception as e:
        return f"РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ: {e}"

def get_pending_approvals() -> list:
    """
    РџРѕР»СѓС‡Р°РµС‚ СЃРїРёСЃРѕРє РѕР¶РёРґР°СЋС‰РёС… РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ Р·Р°СЏРІРѕРє
    """
    try:
        r = requests.get(f"{API_URL.replace('/command', '')}/approvals/pending",
            headers={
                "x-agent-secret": SECRET,
                "Content-Type": "application/json; charset=utf-8"
            },
            timeout=10
        )
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ pending approvals: {e}")
        return []

def format_pending_approvals() -> str:
    """
    Р¤РѕСЂРјР°С‚РёСЂСѓРµС‚ СЃРїРёСЃРѕРє pending approvals РґР»СЏ РѕС‚РїСЂР°РІРєРё РІ Telegram
    """
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

# РџСЂРёРјРµСЂ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ
if __name__ == "__main__":
    print("РўРµСЃС‚ РёРЅС‚РµРіСЂР°С†РёРё СЃ Telegram:")
    print(send_to_agent("РіРґРµ СЏ"))
    print(send_to_agent("Р·Р°РїСѓСЃС‚Рё notepad"))
    print(send_to_agent("РїРѕРєР°Р¶Рё РїСЂРѕС†РµСЃСЃС‹"))
    print("\n" + "="*50)
    print("РўРµСЃС‚ pending approvals:")
    print(format_pending_approvals())
