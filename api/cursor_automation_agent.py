#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Automation Agent
РђРІС‚РѕРЅРѕРјРЅС‹Р№ Р°РіРµРЅС‚ РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ Cursor С‡РµСЂРµР· РіРѕСЂСЏС‡РёРµ РєР»Р°РІРёС€Рё Рё Р°РІС‚РѕРјР°С‚РёР·Р°С†РёСЋ
РЎРѕРіР»Р°СЃРЅРѕ РёРЅСЃС‚СЂСѓРєС†РёСЏРј РїРѕ РёРЅС‚РµРіСЂР°С†РёРё Cursor РґР»СЏ Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р°
"""

import time
import subprocess
import json
import os
import sys
import requests
from pathlib import Path
import pyautogui
import pywinauto
from pywinauto import Application
import logging

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorAutomationAgent:
    """РђРІС‚РѕРЅРѕРјРЅС‹Р№ Р°РіРµРЅС‚ РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ Cursor"""
    
    def __init__(self, project_path="D:/AI-Agent", secret="test123"):
        self.project_path = Path(project_path)
        self.secret = secret
        self.api_base = "http://127.0.0.1:8088"
        self.cursor_window = None
        self.app = None
        
        # РќР°СЃС‚СЂРѕР№РєР° pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        logger.info(f"РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Р°РіРµРЅС‚Р° РґР»СЏ РїСЂРѕРµРєС‚Р°: {self.project_path}")
    
    def start_cursor(self):
        """РЁР°Рі 1: Р—Р°РїСѓСЃРє Cursor Рё РѕС‚РєСЂС‹С‚РёРµ РїСЂРѕРµРєС‚Р°"""
        logger.info("Р—Р°РїСѓСЃРє Cursor...")
        
        try:
            # Р—Р°РїСѓСЃРє Cursor СЃ РїСЂРѕРµРєС‚РѕРј
            cmd = f'cursor "{self.project_path}"'
            subprocess.Popen(cmd, shell=True)
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РіСЂСѓР·РєРё Cursor
            time.sleep(5)
            
            # РџРѕРёСЃРє РѕРєРЅР° Cursor
            self.app = Application().connect(title_re=".*Cursor.*")
            self.cursor_window = self.app.top_window()
            
            logger.info("Cursor СѓСЃРїРµС€РЅРѕ Р·Р°РїСѓС‰РµРЅ")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° Cursor: {e}")
            return False
    
    def focus_cursor_window(self):
        """РЁР°Рі 2: Р¤РѕРєСѓСЃРёСЂРѕРІРєР° РѕРєРЅР° Cursor"""
        logger.info("Р¤РѕРєСѓСЃРёСЂРѕРІРєР° РѕРєРЅР° Cursor...")
        
        try:
            if self.cursor_window:
                self.cursor_window.set_focus()
                time.sleep(1)
                logger.info("РћРєРЅРѕ Cursor СЃС„РѕРєСѓСЃРёСЂРѕРІР°РЅРѕ")
                return True
            else:
                logger.error("РћРєРЅРѕ Cursor РЅРµ РЅР°Р№РґРµРЅРѕ")
                return False
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° С„РѕРєСѓСЃРёСЂРѕРІРєРё: {e}")
            return False
    
    def open_ai_panel(self):
        """РЁР°Рі 3: РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё (Ctrl+L)"""
        logger.info("РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё...")
        
        try:
            # РќР°Р¶Р°С‚РёРµ Ctrl+L РґР»СЏ РѕС‚РєСЂС‹С‚РёСЏ AI-РїР°РЅРµР»Рё
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(2)
            
            logger.info("AI-РїР°РЅРµР»СЊ РѕС‚РєСЂС‹С‚Р°")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РѕС‚РєСЂС‹С‚РёСЏ AI-РїР°РЅРµР»Рё: {e}")
            return False
    
    def switch_to_agent_mode(self):
        """РЁР°Рі 4: РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode"""
        logger.info("РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode...")
        
        try:
            # РџРѕРїС‹С‚РєР° РЅР°Р№С‚Рё Рё РєР»РёРєРЅСѓС‚СЊ РЅР° РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЊ Agent Mode
            # Р•СЃР»Рё РЅРµ СѓРґР°РµС‚СЃСЏ РЅР°Р№С‚Рё, РёСЃРїРѕР»СЊР·СѓРµРј РєРѕРјР°РЅРґРЅСѓСЋ РїР°Р»РёС‚СЂСѓ
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(1)
            
            # Р’РІРѕРґ РєРѕРјР°РЅРґС‹ РґР»СЏ РІРєР»СЋС‡РµРЅРёСЏ Agent Mode
            pyautogui.typewrite("Enable Agent Mode")
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("Agent Mode Р°РєС‚РёРІРёСЂРѕРІР°РЅ")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ РІ Agent Mode: {e}")
            return False
    
    def send_agent_request(self, task_description):
        """РЁР°Рі 5: РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ"""
        logger.info(f"РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ: {task_description}")
        
        try:
            # Р’РІРѕРґ С‚РµРєСЃС‚Р° Р·Р°РґР°С‡Рё РІ РїРѕР»Рµ РІРІРѕРґР°
            pyautogui.typewrite(task_description)
            time.sleep(1)
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° (Enter)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("Р—Р°РїСЂРѕСЃ РѕС‚РїСЂР°РІР»РµРЅ Р°РіРµРЅС‚Сѓ")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РѕС‚РїСЂР°РІРєРё Р·Р°РїСЂРѕСЃР°: {e}")
            return False
    
    def wait_for_agent_completion(self, timeout=300):
        """РЁР°Рі 6: РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°"""
        logger.info("РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # РџСЂРѕРІРµСЂРєР° РЅР° РЅР°Р»РёС‡РёРµ С‚РµРєСЃС‚Р° "Task completed" РёР»Рё РїРѕРґРѕР±РЅРѕРіРѕ
                # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ OCR
                # РёР»Рё Р°РЅР°Р»РёР· СЃРѕРґРµСЂР¶РёРјРѕРіРѕ С‡Р°С‚Р°
                
                # РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РёР·РјРµРЅРµРЅРёР№
                self.auto_confirm_changes()
                
                time.sleep(5)  # РџСЂРѕРІРµСЂРєР° РєР°Р¶РґС‹Рµ 5 СЃРµРєСѓРЅРґ
                
                # Р•СЃР»Рё Р°РіРµРЅС‚ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ (РјРѕР¶РЅРѕ РґРѕР±Р°РІРёС‚СЊ Р±РѕР»РµРµ С‚РѕС‡РЅСѓСЋ РїСЂРѕРІРµСЂРєСѓ)
                if self.check_agent_completion():
                    logger.info("РђРіРµРЅС‚ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ")
                    return True
                    
            except Exception as e:
                logger.error(f"РћС€РёР±РєР° РїСЂРё РѕР¶РёРґР°РЅРёРё: {e}")
                
        logger.warning("РўР°Р№Рј-Р°СѓС‚ РѕР¶РёРґР°РЅРёСЏ Р°РіРµРЅС‚Р°")
        return False
    
    def auto_confirm_changes(self):
        """РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РёР·РјРµРЅРµРЅРёР№"""
        try:
            # РќР°Р¶Р°С‚РёРµ Ctrl+Enter РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ РєРѕРјР°РЅРґ
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(0.5)
            
            # РќР°Р¶Р°С‚РёРµ Enter РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ РёР·РјРµРЅРµРЅРёР№ РєРѕРґР°
            pyautogui.press('enter')
            time.sleep(0.5)
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° Р°РІС‚РѕРїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ: {e}")
    
    def check_agent_completion(self):
        """РџСЂРѕРІРµСЂРєР° Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°"""
        # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ OCR
        # РґР»СЏ Р°РЅР°Р»РёР·Р° СЃРѕРґРµСЂР¶РёРјРѕРіРѕ С‡Р°С‚Р° Рё РїРѕРёСЃРєР° РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ
        return False  # Р—Р°РіР»СѓС€РєР°
    
    def save_all_files(self):
        """РЁР°Рі 7: РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ"""
        logger.info("РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ...")
        
        try:
            # РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ (Ctrl+Shift+S)
            pyautogui.hotkey('ctrl', 'shift', 's')
            time.sleep(1)
            
            logger.info("Р’СЃРµ С„Р°Р№Р»С‹ СЃРѕС…СЂР°РЅРµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° СЃРѕС…СЂР°РЅРµРЅРёСЏ С„Р°Р№Р»РѕРІ: {e}")
            return False
    
    def add_code_comments(self):
        """РЁР°Рі 8: Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ"""
        logger.info("Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ...")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё РґР»СЏ РЅРѕРІРѕРіРѕ Р·Р°РїСЂРѕСЃР°
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(1)
            
            # Р¤РѕСЂРјРёСЂРѕРІР°РЅРёРµ Р·Р°РїСЂРѕСЃР° РЅР° РґРѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ
            comment_request = "Р”РѕР±Р°РІСЊ РїРѕРґСЂРѕР±РЅС‹Рµ РєРѕРјРјРµРЅС‚Р°СЂРёРё Рє РєРѕРґСѓ, РѕР±СЉСЏСЃРЅСЏСЋС‰РёРµ СЂР°Р±РѕС‚Сѓ РєР°Р¶РґРѕР№ С„СѓРЅРєС†РёРё Рё РєР»Р°СЃСЃР° РІ РїСЂРѕРµРєС‚Рµ."
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР°
            pyautogui.typewrite(comment_request)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            self.wait_for_agent_completion(120)
            
            logger.info("РљРѕРјРјРµРЅС‚Р°СЂРёРё РґРѕР±Р°РІР»РµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РґРѕР±Р°РІР»РµРЅРёСЏ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ: {e}")
            return False
    
    def run_tests(self):
        """РЁР°Рі 9: Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ"""
        logger.info("Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ...")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ С‚РµСЂРјРёРЅР°Р»Р° (Ctrl+`)
            pyautogui.hotkey('ctrl', '`')
            time.sleep(1)
            
            # Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            test_command = "py -3.11 -m pytest -q"
            pyautogui.typewrite(test_command)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(5)
            
            logger.info("РўРµСЃС‚С‹ Р·Р°РїСѓС‰РµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° С‚РµСЃС‚РѕРІ: {e}")
            return False
    
    def execute_full_workflow(self, task_description):
        """Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ workflow Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р°"""
        logger.info("=== РќР°С‡Р°Р»Рѕ РїРѕР»РЅРѕРіРѕ workflow Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р° ===")
        
        try:
            # РЁР°Рі 1: Р—Р°РїСѓСЃРє Cursor
            if not self.start_cursor():
                return False
            
            # РЁР°Рі 2: Р¤РѕРєСѓСЃРёСЂРѕРІРєР° РѕРєРЅР°
            if not self.focus_cursor_window():
                return False
            
            # РЁР°Рі 3: РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё
            if not self.open_ai_panel():
                return False
            
            # РЁР°Рі 4: РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode
            if not self.switch_to_agent_mode():
                return False
            
            # РЁР°Рі 5: РћС‚РїСЂР°РІРєР° РѕСЃРЅРѕРІРЅРѕРіРѕ Р·Р°РїСЂРѕСЃР°
            if not self.send_agent_request(task_description):
                return False
            
            # РЁР°Рі 6: РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            if not self.wait_for_agent_completion():
                logger.warning("РђРіРµРЅС‚ РЅРµ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ РІ РѕР¶РёРґР°РµРјРѕРµ РІСЂРµРјСЏ")
            
            # РЁР°Рі 7: РЎРѕС…СЂР°РЅРµРЅРёРµ С„Р°Р№Р»РѕРІ
            self.save_all_files()
            
            # РЁР°Рі 8: Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ
            self.add_code_comments()
            
            # РЁР°Рі 9: Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            self.run_tests()
            
            logger.info("=== Workflow Р·Р°РІРµСЂС€РµРЅ СѓСЃРїРµС€РЅРѕ ===")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РІ workflow: {e}")
            return False
    
    def check_api_health(self):
        """РџСЂРѕРІРµСЂРєР° Р·РґРѕСЂРѕРІСЊСЏ API Р°РіРµРЅС‚Р°"""
        try:
            headers = {"x-agent-secret": self.secret}
            response = requests.get(f"{self.api_base}/health", headers=headers, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"API Р·РґРѕСЂРѕРІ: {response.json()}")
                return True
            else:
                logger.error(f"API РЅРµ РѕС‚РІРµС‡Р°РµС‚: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РїСЂРѕРІРµСЂРєРё API: {e}")
            return False
    
    def start_api_agent(self):
        """Р—Р°РїСѓСЃРє API Р°РіРµРЅС‚Р°"""
        logger.info("Р—Р°РїСѓСЃРє API Р°РіРµРЅС‚Р°...")
        
        try:
            # Р—Р°РїСѓСЃРє API Р°РіРµРЅС‚Р° С‡РµСЂРµР· PowerShell СЃРєСЂРёРїС‚
            script_path = self.project_path / "start_agent_final.ps1"
            
            if script_path.exists():
                subprocess.Popen([
                    "powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)
                ], shell=True)
                
                # РћР¶РёРґР°РЅРёРµ Р·Р°РїСѓСЃРєР° API
                time.sleep(10)
                
                # РџСЂРѕРІРµСЂРєР° Р·РґРѕСЂРѕРІСЊСЏ
                if self.check_api_health():
                    logger.info("API Р°РіРµРЅС‚ Р·Р°РїСѓС‰РµРЅ Рё СЂР°Р±РѕС‚Р°РµС‚")
                    return True
                else:
                    logger.error("API Р°РіРµРЅС‚ РЅРµ РѕС‚РІРµС‡Р°РµС‚")
                    return False
            else:
                logger.error(f"РЎРєСЂРёРїС‚ РЅРµ РЅР°Р№РґРµРЅ: {script_path}")
                return False
                
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° API Р°РіРµРЅС‚Р°: {e}")
            return False

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    logger.info("Р—Р°РїСѓСЃРє Cursor Automation Agent")
    
    # РЎРѕР·РґР°РЅРёРµ Р°РіРµРЅС‚Р°
    agent = CursorAutomationAgent()
    
    # Р—Р°РїСѓСЃРє API Р°РіРµРЅС‚Р°
    if not agent.start_api_agent():
        logger.error("РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РїСѓСЃС‚РёС‚СЊ API Р°РіРµРЅС‚Р°")
        return False
    
    # РџСЂРёРјРµСЂ Р·Р°РґР°С‡Рё РґР»СЏ Р°РіРµРЅС‚Р°
    task = """
    РЎРѕР·РґР°Р№ РїРѕР»РЅРѕС„СѓРЅРєС†РёРѕРЅР°Р»СЊРЅРѕРµ РІРµР±-РїСЂРёР»РѕР¶РµРЅРёРµ РЅР° FastAPI СЃ PostgreSQL Р±Р°Р·РѕР№ РґР°РЅРЅС‹С….
    Р’РєР»СЋС‡Рё:
    1. РњРѕРґРµР»Рё РґР°РЅРЅС‹С… РґР»СЏ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ Рё Р·Р°РґР°С‡
    2. API endpoints РґР»СЏ CRUD РѕРїРµСЂР°С†РёР№
    3. РђСѓС‚РµРЅС‚РёС„РёРєР°С†РёСЋ Рё Р°РІС‚РѕСЂРёР·Р°С†РёСЋ
    4. Р”РѕРєСѓРјРµРЅС‚Р°С†РёСЋ API
    5. Docker РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ
    6. РўРµСЃС‚С‹ РґР»СЏ РІСЃРµС… РєРѕРјРїРѕРЅРµРЅС‚РѕРІ
    7. РџРѕРґСЂРѕР±РЅС‹Рµ РєРѕРјРјРµРЅС‚Р°СЂРёРё Рє РєРѕРґСѓ
    """
    
    # Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ workflow
    success = agent.execute_full_workflow(task)
    
    if success:
        logger.info("РџСЂРѕРµРєС‚ СѓСЃРїРµС€РЅРѕ Р·Р°РІРµСЂС€РµРЅ!")
    else:
        logger.error("РџСЂРѕРёР·РѕС€Р»Рё РѕС€РёР±РєРё РІ РїСЂРѕС†РµСЃСЃРµ РІС‹РїРѕР»РЅРµРЅРёСЏ")
    
    return success

if __name__ == "__main__":
    main()

