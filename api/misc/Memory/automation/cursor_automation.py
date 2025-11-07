# Cursor Automation - Python СЃРєСЂРёРїС‚ РґР»СЏ Р°РІС‚РѕРјР°С‚РёР·Р°С†РёРё Cursor Editor
# РСЃРїРѕР»СЊР·СѓРµС‚ pyautogui РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ РёРЅС‚РµСЂС„РµР№СЃРѕРј

import pyautogui
import time
import json
import os
import sys
from typing import Optional

class CursorAutomation:
    def __init__(self, project_path: str = "D:\\AI-Agent\\fresh_start"):
        self.project_path = project_path
        self.cursor_window = None
        
        # РќР°СЃС‚СЂРѕР№РєРё pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
    def find_cursor_window(self) -> bool:
        """РџРѕРёСЃРє РѕРєРЅР° Cursor"""
        try:
            # РџРѕР»СѓС‡Р°РµРј СЃРїРёСЃРѕРє РѕРєРѕРЅ
            windows = pyautogui.getAllWindows()
            
            for window in windows:
                if window.title and "cursor" in window.title.lower():
                    self.cursor_window = window
                    return True
            
            return False
        except Exception as e:
            print(f"Error finding Cursor window: {e}")
            return False
    
    def focus_cursor(self) -> bool:
        """Р¤РѕРєСѓСЃ РЅР° РѕРєРЅРµ Cursor"""
        try:
            if self.cursor_window:
                self.cursor_window.activate()
                time.sleep(1)
                return True
            return False
        except Exception as e:
            print(f"Error focusing Cursor: {e}")
            return False
    
    def open_terminal(self) -> bool:
        """РћС‚РєСЂС‹С‚РёРµ С‚РµСЂРјРёРЅР°Р»Р° С‡РµСЂРµР· РїР°Р»РёС‚СЂСѓ РєРѕРјР°РЅРґ"""
        try:
            # РћС‚РєСЂС‹РІР°РµРј РїР°Р»РёС‚СЂСѓ РєРѕРјР°РЅРґ
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(1)
            
            # Р’РІРѕРґРёРј РєРѕРјР°РЅРґСѓ РґР»СЏ С‚РµСЂРјРёРЅР°Р»Р°
            pyautogui.typewrite("Terminal: New Terminal")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"Error opening terminal: {e}")
            return False
    
    def send_task_to_agent(self, task: str) -> bool:
        """РћС‚РїСЂР°РІРєР° Р·Р°РґР°С‡Рё Р°РіРµРЅС‚Сѓ"""
        try:
            # РћС‡РёС‰Р°РµРј С‚РµСЂРјРёРЅР°Р»
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # Р’РІРѕРґРёРј Р·Р°РґР°С‡Сѓ
            pyautogui.typewrite(task)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"Error sending task: {e}")
            return False
    
    def auto_confirm_prompts(self, count: int = 5) -> bool:
        """РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РїСЂРѕРјРїС‚РѕРІ"""
        try:
            for _ in range(count):
                pyautogui.press('enter')
                pyautogui.press('tab')
                time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"Error auto-confirming: {e}")
            return False
    
    def save_and_commit(self, message: str = "Auto commit") -> bool:
        """РЎРѕС…СЂР°РЅРµРЅРёРµ Рё РєРѕРјРјРёС‚ РёР·РјРµРЅРµРЅРёР№"""
        try:
            # РЎРѕС…СЂР°РЅСЏРµРј С„Р°Р№Р»С‹
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            
            # РћС‚РєСЂС‹РІР°РµРј Git РїР°РЅРµР»СЊ
            pyautogui.hotkey('ctrl', 'shift', 'g')
            time.sleep(1)
            
            # Р’РІРѕРґРёРј СЃРѕРѕР±С‰РµРЅРёРµ РєРѕРјРјРёС‚Р°
            pyautogui.typewrite(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"Error saving and committing: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ"""
        try:
            # РћС‚РєСЂС‹РІР°РµРј РЅРѕРІС‹Р№ С‚РµСЂРјРёРЅР°Р»
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(0.5)
            pyautogui.typewrite("Terminal: New Terminal")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1.5)
            
            # РћС‡РёС‰Р°РµРј С‚РµСЂРјРёРЅР°Р»
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # Р—Р°РїСѓСЃРєР°РµРј С‚РµСЃС‚С‹
            pyautogui.typewrite("python -m pytest -q")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(5)
            
            return True
        except Exception as e:
            print(f"Error running tests: {e}")
            return False
    
    def execute_task(self, task: str) -> bool:
        """Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕР№ Р·Р°РґР°С‡Рё"""
        try:
            print(f"Executing task: {task}")
            
            # РќР°С…РѕРґРёРј Рё С„РѕРєСѓСЃРёСЂСѓРµРјСЃСЏ РЅР° Cursor
            if not self.find_cursor_window():
                print("Cursor window not found")
                return False
            
            if not self.focus_cursor():
                print("Failed to focus Cursor")
                return False
            
            # РћС‚РєСЂС‹РІР°РµРј С‚РµСЂРјРёРЅР°Р»
            if not self.open_terminal():
                print("Failed to open terminal")
                return False
            
            # РћС‚РїСЂР°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ
            if not self.send_task_to_agent(task):
                print("Failed to send task")
                return False
            
            # РђРІС‚РѕРїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ
            self.auto_confirm_prompts()
            
            # РЎРѕС…СЂР°РЅСЏРµРј Рё РєРѕРјРјРёС‚РёРј
            self.save_and_commit()
            
            # Р—Р°РїСѓСЃРєР°РµРј С‚РµСЃС‚С‹
            self.run_tests()
            
            print("Task executed successfully")
            return True
            
        except Exception as e:
            print(f"Error executing task: {e}")
            return False

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    if len(sys.argv) < 2:
        print("Usage: python cursor_automation.py <task>")
        sys.exit(1)
    
    task = sys.argv[1]
    automation = CursorAutomation()
    
    success = automation.execute_task(task)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()





