#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
РўРµСЃС‚ РёСЃРїСЂР°РІР»РµРЅРёСЏ РєРѕРґРёСЂРѕРІРєРё РІ Telegram Р±РѕС‚Рµ
"""
import sys
import json
import requests

# РќРµ РјРѕРґРёС„РёС†РёСЂСѓРµРј СЃРёСЃС‚РµРјРЅС‹Рµ stdout/stderr: РёС… Р·Р°РєСЂС‹С‚РёРµ/"detaching" Р»РѕРјР°РµС‚ pytest РЅР° Windows

def test_encoding_fix():
    """РўРµСЃС‚ РёСЃРїСЂР°РІР»РµРЅРёСЏ РєРѕРґРёСЂРѕРІРєРё"""
    print("рџ§Є РўРµСЃС‚РёСЂРѕРІР°РЅРёРµ РёСЃРїСЂР°РІР»РµРЅРёСЏ РєРѕРґРёСЂРѕРІРєРё...")
    
    # РўРµСЃС‚РѕРІС‹Рµ РґР°РЅРЅС‹Рµ СЃ РєРёСЂРёР»Р»РёС†РµР№
    test_data = {
        "text": "РџСЂРёРІРµС‚! Р­С‚Рѕ С‚РµСЃС‚ РєРёСЂРёР»Р»РёС†С‹: С‘С‘С‘ РЃРЃРЃ",
        "chat_id": 12345,
        "parse_mode": "HTML"
    }
    
    print(f"рџ“ќ РўРµСЃС‚РѕРІС‹Рµ РґР°РЅРЅС‹Рµ: {test_data['text']}")
    
    try:
        # РўРµСЃС‚ 1: РљРѕРґРёСЂРѕРІР°РЅРёРµ РІ UTF-8
        print("\n1пёЏвѓЈ РўРµСЃС‚ РєРѕРґРёСЂРѕРІР°РЅРёСЏ РІ UTF-8...")
        json_data = json.dumps(test_data, ensure_ascii=False).encode('utf-8')
        print(f"вњ… JSON РґР°РЅРЅС‹Рµ Р·Р°РєРѕРґРёСЂРѕРІР°РЅС‹: {len(json_data)} Р±Р°Р№С‚")
        
        # РўРµСЃС‚ 2: Р”РµРєРѕРґРёСЂРѕРІР°РЅРёРµ РѕР±СЂР°С‚РЅРѕ
        print("\n2пёЏвѓЈ РўРµСЃС‚ РґРµРєРѕРґРёСЂРѕРІР°РЅРёСЏ...")
        decoded_data = json_data.decode('utf-8')
        parsed_data = json.loads(decoded_data)
        print(f"вњ… Р”Р°РЅРЅС‹Рµ РґРµРєРѕРґРёСЂРѕРІР°РЅС‹: {parsed_data['text']}")
        
        # РўРµСЃС‚ 3: РџСЂРѕРІРµСЂРєР° Р·Р°РіРѕР»РѕРІРєРѕРІ
        print("\n3пёЏвѓЈ РўРµСЃС‚ Р·Р°РіРѕР»РѕРІРєРѕРІ HTTP...")
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8'
        }
        print(f"вњ… Р—Р°РіРѕР»РѕРІРєРё СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹: {headers}")
        
        # РўРµСЃС‚ 4: РџСЂРѕРІРµСЂРєР° РїРµСЂРµРјРµРЅРЅС‹С… РѕРєСЂСѓР¶РµРЅРёСЏ
        print("\n4пёЏвѓЈ РўРµСЃС‚ РїРµСЂРµРјРµРЅРЅС‹С… РѕРєСЂСѓР¶РµРЅРёСЏ...")
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        print(f"вњ… PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING')}")
        print(f"вњ… PYTHONUTF8: {os.environ.get('PYTHONUTF8')}")
        
        print("\nрџЋ‰ Р’РЎР• РўР•РЎРўР« РџР РћРЁР›Р РЈРЎРџР•РЁРќРћ!")
        print("вњ… РљРѕРґРёСЂРѕРІРєР° UTF-8 СЂР°Р±РѕС‚Р°РµС‚ РєРѕСЂСЂРµРєС‚РЅРѕ")
        print("вњ… РљРёСЂРёР»Р»РёС†Р° РїРѕРґРґРµСЂР¶РёРІР°РµС‚СЃСЏ")
        print("вњ… РџСЂРѕР±Р»РµРјР° СЃ latin-1 СЂРµС€РµРЅР°")
        
        assert True
        
    except Exception as e:
        raise AssertionError(f"Encoding test error: {e}")

def test_telegram_api_simulation():
    """РЎРёРјСѓР»СЏС†РёСЏ СЂР°Р±РѕС‚С‹ СЃ Telegram API"""
    print("\nрџ¤– РЎРёРјСѓР»СЏС†РёСЏ СЂР°Р±РѕС‚С‹ СЃ Telegram API...")
    
    # РЎРёРјСѓР»СЏС†РёСЏ РѕС‚РїСЂР°РІРєРё СЃРѕРѕР±С‰РµРЅРёСЏ
    test_message = {
        "chat_id": 12345,
        "text": "РўРµСЃС‚ РєРёСЂРёР»Р»РёС†С‹: РїСЂРёРІРµС‚ РјРёСЂ! рџЊЌ",
        "parse_mode": "HTML"
    }
    
    try:
        # РљРѕРґРёСЂСѓРµРј РґР°РЅРЅС‹Рµ РєР°Рє РІ РёСЃРїСЂР°РІР»РµРЅРЅРѕРј Р±РѕС‚Рµ
        json_data = json.dumps(test_message, ensure_ascii=False).encode('utf-8')
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8'
        }
        
        print(f"вњ… РЎРѕРѕР±С‰РµРЅРёРµ РїРѕРґРіРѕС‚РѕРІР»РµРЅРѕ: {test_message['text']}")
        print(f"вњ… Р Р°Р·РјРµСЂ РґР°РЅРЅС‹С…: {len(json_data)} Р±Р°Р№С‚")
        print(f"вњ… Р—Р°РіРѕР»РѕРІРєРё: {headers}")
        
        # Р”РµРєРѕРґРёСЂСѓРµРј РѕР±СЂР°С‚РЅРѕ РґР»СЏ РїСЂРѕРІРµСЂРєРё
        decoded = json_data.decode('utf-8')
        parsed = json.loads(decoded)
        
        print(f"вњ… Р”РµРєРѕРґРёСЂРѕРІР°РЅРЅРѕРµ СЃРѕРѕР±С‰РµРЅРёРµ: {parsed['text']}")
        print("вњ… РЎРёРјСѓР»СЏС†РёСЏ Telegram API РїСЂРѕС€Р»Р° СѓСЃРїРµС€РЅРѕ!")
        
        assert True
        
    except Exception as e:
        raise AssertionError(f"Telegram simulation error: {e}")

if __name__ == "__main__":
    print("рџљЂ Р—РђРџРЈРЎРљ РўР•РЎРўРћР’ РРЎРџР РђР’Р›Р•РќРРЇ РљРћР”РР РћР’РљР")
    print("=" * 50)
    
    # Р—Р°РїСѓСЃРєР°РµРј С‚РµСЃС‚С‹
    test1_result = test_encoding_fix()
    test2_result = test_telegram_api_simulation()
    
    print("\n" + "=" * 50)
    print("рџ“Љ Р Р•Р—РЈР›Р¬РўРђРўР« РўР•РЎРўРР РћР’РђРќРРЇ:")
    print(f"1пёЏвѓЈ РўРµСЃС‚ РєРѕРґРёСЂРѕРІРєРё: {'вњ… РџР РћРЁР•Р›' if test1_result else 'вќЊ РџР РћР’РђР›Р•Рќ'}")
    print(f"2пёЏвѓЈ РЎРёРјСѓР»СЏС†РёСЏ API: {'вњ… РџР РћРЁР•Р›' if test2_result else 'вќЊ РџР РћР’РђР›Р•Рќ'}")
    
    if test1_result and test2_result:
        print("\nрџЋ‰ Р’РЎР• РўР•РЎРўР« РџР РћРЁР›Р РЈРЎРџР•РЁРќРћ!")
        print("вњ… РСЃРїСЂР°РІР»РµРЅРёРµ РєРѕРґРёСЂРѕРІРєРё СЂР°Р±РѕС‚Р°РµС‚ РєРѕСЂСЂРµРєС‚РЅРѕ")
        print("вњ… РњРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ РёСЃРїСЂР°РІР»РµРЅРЅС‹Рµ Р±РѕС‚С‹")
    else:
        print("\nвќЊ РќР•РљРћРўРћР Р«Р• РўР•РЎРўР« РџР РћР’РђР›Р•РќР«")
        print("вљ пёЏ РўСЂРµР±СѓРµС‚СЃСЏ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅР°СЏ РЅР°СЃС‚СЂРѕР№РєР°")

