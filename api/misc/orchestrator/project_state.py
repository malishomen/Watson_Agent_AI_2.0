# -*- coding: utf-8 -*-
"""
Project State Management
РЈРїСЂР°РІР»РµРЅРёРµ СЃРѕСЃС‚РѕСЏРЅРёРµРј РїСЂРѕРµРєС‚РѕРІ
"""
import json, os

BASE = "D:/AI-Agent/Projects"

def _state_path(pid):
    """РџСѓС‚СЊ Рє С„Р°Р№Р»Сѓ СЃРѕСЃС‚РѕСЏРЅРёСЏ РїСЂРѕРµРєС‚Р°"""
    return os.path.join(BASE, pid, "state.json")

def load_state(pid):
    """Р—Р°РіСЂСѓР¶Р°РµС‚ СЃРѕСЃС‚РѕСЏРЅРёРµ РїСЂРѕРµРєС‚Р°"""
    try:
        with open(_state_path(pid), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "state": "new",
            "current_step": 0,
            "total_steps": 0,
            "errors": [],
            "last_message": ""
        }

def save_state(pid, state):
    """РЎРѕС…СЂР°РЅСЏРµС‚ СЃРѕСЃС‚РѕСЏРЅРёРµ РїСЂРѕРµРєС‚Р°"""
    os.makedirs(os.path.join(BASE, pid), exist_ok=True)
    with open(_state_path(pid), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def reset_state(pid):
    """РЎР±СЂР°СЃС‹РІР°РµС‚ СЃРѕСЃС‚РѕСЏРЅРёРµ РїСЂРѕРµРєС‚Р°"""
    save_state(pid, {
        "state": "new",
        "current_step": 0,
        "total_steps": 0,
        "errors": [],
        "last_message": ""
    })
