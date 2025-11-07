# Execute Tasks - РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РІС‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡ РІ Cursor
# РРЅС‚РµРіСЂР°С†РёСЏ СЃ API Р°РіРµРЅС‚РѕРј Рё Р°РІС‚РѕРјР°С‚РёР·Р°С†РёСЏ Cursor

import requests
import json
import os
import time
import subprocess
import pyautogui
from pathlib import Path

def get_pending_tasks():
    """РџРѕР»СѓС‡РµРЅРёРµ СЃРїРёСЃРєР° РѕР¶РёРґР°СЋС‰РёС… Р·Р°РґР°С‡"""
    try:
        # РџРѕР»СѓС‡Р°РµРј СЃРїРёСЃРѕРє С„Р°Р№Р»РѕРІ Р·Р°РґР°С‡
        tasks_dir = Path("tasks")
        if not tasks_dir.exists():
            return []
        
        pending_tasks = []
        for task_file in tasks_dir.glob("*.json"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                    if task_data.get("status") == "pending":
                        pending_tasks.append({
                            "file": task_file,
                            "data": task_data
                        })
            except Exception as e:
                print(f"вќЊ РћС€РёР±РєР° С‡С‚РµРЅРёСЏ Р·Р°РґР°С‡Рё {task_file}: {e}")
        
        return pending_tasks
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ Р·Р°РґР°С‡: {e}")
        return []

def start_cursor():
    """Р—Р°РїСѓСЃРє Cursor"""
    try:
        print("рџљЂ Р—Р°РїСѓСЃРє Cursor...")
        
        # Р—Р°РїСѓСЃРєР°РµРј Cursor СЃ С‚РµРєСѓС‰РµР№ РґРёСЂРµРєС‚РѕСЂРёРµР№
        process = subprocess.Popen([
            "cursor", "."
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Р–РґРµРј Р·Р°РїСѓСЃРєР°
        time.sleep(5)
        
        print("вњ… Cursor Р·Р°РїСѓС‰РµРЅ")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° Cursor: {e}")
        return False

def execute_task_in_cursor(task_description):
    """Р’С‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡Рё РІ Cursor"""
    try:
        print(f"рџ“ќ Р’С‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡Рё: {task_description}")
        
        # РќР°СЃС‚СЂРѕР№РєРё pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1
        
        # Р–РґРµРј С„РѕРєСѓСЃР° РЅР° Cursor
        time.sleep(2)
        
        # РћС‚РєСЂС‹РІР°РµРј С‚РµСЂРјРёРЅР°Р» С‡РµСЂРµР· РїР°Р»РёС‚СЂСѓ РєРѕРјР°РЅРґ
        pyautogui.hotkey('ctrl', 'shift', 'p')
        time.sleep(1)
        pyautogui.typewrite("Terminal: New Terminal")
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        # РћС‡РёС‰Р°РµРј С‚РµСЂРјРёРЅР°Р»
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        
        # РћС‚РїСЂР°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ Р°РіРµРЅС‚Сѓ
        pyautogui.typewrite(f"# Р—Р°РґР°С‡Р°: {task_description}")
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)
        
        # РЎРѕР·РґР°РµРј РїСЂРѕСЃС‚РѕР№ С„Р°Р№Р» РґР»СЏ РґРµРјРѕРЅСЃС‚СЂР°С†РёРё
        pyautogui.typewrite(f"echo '# {task_description}' > task_{int(time.time())}.md")
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)
        
        # РЎРѕС…СЂР°РЅСЏРµРј С„Р°Р№Р»С‹
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1)
        
        print("вњ… Р—Р°РґР°С‡Р° РІС‹РїРѕР»РЅРµРЅР° РІ Cursor")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РІС‹РїРѕР»РЅРµРЅРёСЏ Р·Р°РґР°С‡Рё: {e}")
        return False

def mark_task_completed(task_file, task_data):
    """РћС‚РјРµС‚РєР° Р·Р°РґР°С‡Рё РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅРѕР№"""
    try:
        task_data["status"] = "completed"
        task_data["completed_at"] = time.time()
        
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        print(f"вњ… Р—Р°РґР°С‡Р° {task_file.name} РѕС‚РјРµС‡РµРЅР° РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅР°СЏ")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РѕС‚РјРµС‚РєРё Р·Р°РґР°С‡Рё: {e}")
        return False

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    print("рџ¤– Execute Tasks - РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РІС‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡")
    print("=" * 60)
    
    # РџСЂРѕРІРµСЂСЏРµРј API Р°РіРµРЅС‚
    try:
        response = requests.get("http://127.0.0.1:8088/health", timeout=5)
        if response.status_code != 200:
            print("вќЊ API Р°РіРµРЅС‚ РЅРµ СЂР°Р±РѕС‚Р°РµС‚")
            return
    except:
        print("вќЊ API Р°РіРµРЅС‚ РЅРµРґРѕСЃС‚СѓРїРµРЅ")
        return
    
    # РџРѕР»СѓС‡Р°РµРј РѕР¶РёРґР°СЋС‰РёРµ Р·Р°РґР°С‡Рё
    pending_tasks = get_pending_tasks()
    
    if not pending_tasks:
        print("рџ“‹ РќРµС‚ РѕР¶РёРґР°СЋС‰РёС… Р·Р°РґР°С‡")
        return
    
    print(f"рџ“‹ РќР°Р№РґРµРЅРѕ Р·Р°РґР°С‡: {len(pending_tasks)}")
    
    # Р—Р°РїСѓСЃРєР°РµРј Cursor
    if not start_cursor():
        print("вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РїСѓСЃС‚РёС‚СЊ Cursor")
        return
    
    # Р’С‹РїРѕР»РЅСЏРµРј Р·Р°РґР°С‡Рё
    completed_tasks = 0
    for task_info in pending_tasks:
        task_file = task_info["file"]
        task_data = task_info["data"]
        task_description = task_data.get("task", "РќРµРёР·РІРµСЃС‚РЅР°СЏ Р·Р°РґР°С‡Р°")
        
        print(f"\n--- Р’С‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡Рё ---")
        print(f"рџ“ќ РћРїРёСЃР°РЅРёРµ: {task_description}")
        
        # Р’С‹РїРѕР»РЅСЏРµРј Р·Р°РґР°С‡Сѓ РІ Cursor
        if execute_task_in_cursor(task_description):
            # РћС‚РјРµС‡Р°РµРј РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅСѓСЋ
            if mark_task_completed(task_file, task_data):
                completed_tasks += 1
        else:
            print(f"вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ РІС‹РїРѕР»РЅРёС‚СЊ Р·Р°РґР°С‡Сѓ")
        
        # РџР°СѓР·Р° РјРµР¶РґСѓ Р·Р°РґР°С‡Р°РјРё
        time.sleep(2)
    
    print(f"\n" + "=" * 60)
    print(f"рџ“Љ Р РµР·СѓР»СЊС‚Р°С‚:")
    print(f"вњ… Р’С‹РїРѕР»РЅРµРЅРѕ Р·Р°РґР°С‡: {completed_tasks}")
    print(f"рџ“ќ Р’СЃРµРіРѕ Р·Р°РґР°С‡: {len(pending_tasks)}")
    
    if completed_tasks > 0:
        print(f"\nрџЋЇ Р—Р°РґР°С‡Рё РІС‹РїРѕР»РЅРµРЅС‹ РІ Cursor!")
        print(f"рџ’Ў РџСЂРѕРІРµСЂСЊС‚Рµ Cursor - С‚Р°Рј РґРѕР»Р¶РЅС‹ РїРѕСЏРІРёС‚СЊСЃСЏ РЅРѕРІС‹Рµ С„Р°Р№Р»С‹")

if __name__ == "__main__":
    main()





