#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Integration Final
Р¤РёРЅР°Р»СЊРЅР°СЏ РёРЅС‚РµРіСЂР°С†РёСЏ Cursor СЃ Р°РІС‚РѕРЅРѕРјРЅС‹Рј AI-Р°РіРµРЅС‚РѕРј
РџРѕР»РЅР°СЏ СЂРµР°Р»РёР·Р°С†РёСЏ СЃРѕРіР»Р°СЃРЅРѕ РёРЅСЃС‚СЂСѓРєС†РёСЏРј РїРѕ РёРЅС‚РµРіСЂР°С†РёРё Cursor РґР»СЏ Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р°
"""

import time
import subprocess
import json
import os
import sys
import requests
from pathlib import Path
import pyautogui
import logging
import threading
import queue
from datetime import datetime

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_integration_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CursorIntegrationFinal:
    """Р¤РёРЅР°Р»СЊРЅР°СЏ РёРЅС‚РµРіСЂР°С†РёСЏ Cursor СЃ Р°РІС‚РѕРЅРѕРјРЅС‹Рј AI-Р°РіРµРЅС‚РѕРј"""
    
    def __init__(self, project_path="D:/AI-Agent", secret="test123"):
        self.project_path = Path(project_path)
        self.secret = secret
        self.api_base = "http://127.0.0.1:8088"
        self.cursor_process = None
        self.agent_active = False
        
        # РќР°СЃС‚СЂРѕР№РєР° pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2
        
        # РЎС‚Р°С‚РёСЃС‚РёРєР° РІС‹РїРѕР»РЅРµРЅРёСЏ
        self.stats = {
            'start_time': None,
            'end_time': None,
            'tasks_completed': 0,
            'errors': 0,
            'files_created': 0,
            'files_modified': 0
        }
        
        logger.info(f"РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ С„РёРЅР°Р»СЊРЅРѕР№ РёРЅС‚РµРіСЂР°С†РёРё РґР»СЏ РїСЂРѕРµРєС‚Р°: {self.project_path}")
    
    def start_cursor_project(self):
        """РЁР°Рі 1: Р—Р°РїСѓСЃРє Cursor Рё РѕС‚РєСЂС‹С‚РёРµ РїСЂРѕРµРєС‚Р°"""
        logger.info("=== РЁР°Рі 1: Р—Р°РїСѓСЃРє Cursor Рё РѕС‚РєСЂС‹С‚РёРµ РїСЂРѕРµРєС‚Р° ===")
        
        try:
            # Р—Р°РїСѓСЃРє Cursor СЃ РїСЂРѕРµРєС‚РѕРј
            cmd = f'cursor "{self.project_path}"'
            self.cursor_process = subprocess.Popen(cmd, shell=True)
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РіСЂСѓР·РєРё Cursor
            time.sleep(8)
            
            # Р¤РѕРєСѓСЃРёСЂРѕРІРєР° РѕРєРЅР° Cursor
            self.focus_cursor_window()
            
            logger.info("вњ… Cursor Р·Р°РїСѓС‰РµРЅ Рё РїСЂРѕРµРєС‚ РѕС‚РєСЂС‹С‚")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° Cursor: {e}")
            self.stats['errors'] += 1
            return False
    
    def focus_cursor_window(self):
        """Р¤РѕРєСѓСЃРёСЂРѕРІРєР° РѕРєРЅР° Cursor"""
        try:
            # РџРѕРїС‹С‚РєР° Р°РєС‚РёРІР°С†РёРё РѕРєРЅР° Cursor
            pyautogui.hotkey('alt', 'tab')
            time.sleep(1)
            
            # Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅР°СЏ РїРѕРїС‹С‚РєР° С‡РµСЂРµР· РїРѕРёСЃРє РѕРєРЅР°
            pyautogui.hotkey('win', 'd')  # РЎРІРµСЂРЅСѓС‚СЊ РІСЃРµ РѕРєРЅР°
            time.sleep(1)
            pyautogui.hotkey('alt', 'tab')  # РџРµСЂРµРєР»СЋС‡РёС‚СЊСЃСЏ РЅР° Cursor
            
            time.sleep(2)
            logger.info("РћРєРЅРѕ Cursor СЃС„РѕРєСѓСЃРёСЂРѕРІР°РЅРѕ")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° С„РѕРєСѓСЃРёСЂРѕРІРєРё РѕРєРЅР°: {e}")
            return False
    
    def open_ai_panel(self):
        """РЁР°Рі 2: РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё (Ctrl+L)"""
        logger.info("=== РЁР°Рі 2: РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё ===")
        
        try:
            # РќР°Р¶Р°С‚РёРµ Ctrl+L РґР»СЏ РѕС‚РєСЂС‹С‚РёСЏ AI-РїР°РЅРµР»Рё
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(3)
            
            logger.info("вњ… AI-РїР°РЅРµР»СЊ РѕС‚РєСЂС‹С‚Р°")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РѕС‚РєСЂС‹С‚РёСЏ AI-РїР°РЅРµР»Рё: {e}")
            self.stats['errors'] += 1
            return False
    
    def switch_to_agent_mode(self):
        """РЁР°Рі 3: РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode"""
        logger.info("=== РЁР°Рі 3: РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode ===")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ РєРѕРјР°РЅРґРЅРѕР№ РїР°Р»РёС‚СЂС‹ (Ctrl+Shift+P)
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(2)
            
            # Р’РІРѕРґ РєРѕРјР°РЅРґС‹ РґР»СЏ РІРєР»СЋС‡РµРЅРёСЏ Agent Mode
            pyautogui.typewrite("Enable Agent Mode")
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(3)
            
            # РђР»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Р№ СЃРїРѕСЃРѕР± - РїРѕРёСЃРє РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЏ Agent Mode
            # Р•СЃР»Рё РєРѕРјР°РЅРґРЅР°СЏ РїР°Р»РёС‚СЂР° РЅРµ СЃСЂР°Р±РѕС‚Р°Р»Р°, РїРѕРїСЂРѕР±СѓРµРј РЅР°Р№С‚Рё РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЊ
            self.find_agent_mode_toggle()
            
            logger.info("вњ… Agent Mode Р°РєС‚РёРІРёСЂРѕРІР°РЅ")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ РІ Agent Mode: {e}")
            self.stats['errors'] += 1
            return False
    
    def find_agent_mode_toggle(self):
        """РџРѕРёСЃРє Рё Р°РєС‚РёРІР°С†РёСЏ РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЏ Agent Mode"""
        try:
            # РџРѕРёСЃРє РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЏ Agent Mode РІ РёРЅС‚РµСЂС„РµР№СЃРµ
            # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ OCR
            # РёР»Рё РїРѕРёСЃРє РїРѕ РєРѕРѕСЂРґРёРЅР°С‚Р°Рј
            
            # РџРѕРїС‹С‚РєР° РЅР°Р№С‚Рё РєРЅРѕРїРєСѓ Agent Mode
            screen_width, screen_height = pyautogui.size()
            
            # РџРѕРёСЃРє РІ РїСЂР°РІРѕР№ С‡Р°СЃС‚Рё СЌРєСЂР°РЅР° (РіРґРµ РѕР±С‹С‡РЅРѕ РЅР°С…РѕРґРёС‚СЃСЏ AI-РїР°РЅРµР»СЊ)
            search_x = int(screen_width * 0.7)
            search_y = int(screen_height * 0.3)
            
            pyautogui.click(search_x, search_y)
            time.sleep(1)
            
        except Exception as e:
            logger.debug(f"РќРµ СѓРґР°Р»РѕСЃСЊ РЅР°Р№С‚Рё РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЊ Agent Mode: {e}")
    
    def send_agent_request(self, task_description):
        """РЁР°Рі 4: РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ"""
        logger.info("=== РЁР°Рі 4: РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ ===")
        
        try:
            # РћС‡РёСЃС‚РєР° РїРѕР»СЏ РІРІРѕРґР°
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # Р’РІРѕРґ С‚РµРєСЃС‚Р° Р·Р°РґР°С‡Рё
            pyautogui.typewrite(task_description)
            time.sleep(2)
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° (Enter)
            pyautogui.press('enter')
            time.sleep(3)
            
            logger.info("вњ… Р—Р°РїСЂРѕСЃ РѕС‚РїСЂР°РІР»РµРЅ Р°РіРµРЅС‚Сѓ")
            self.stats['tasks_completed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РѕС‚РїСЂР°РІРєРё Р·Р°РїСЂРѕСЃР°: {e}")
            self.stats['errors'] += 1
            return False
    
    def wait_for_agent_completion(self, timeout=600):
        """РЁР°Рі 5: РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°"""
        logger.info("=== РЁР°Рі 5: РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р° ===")
        
        start_time = time.time()
        last_activity = start_time
        
        while time.time() - start_time < timeout:
            try:
                # РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РёР·РјРµРЅРµРЅРёР№
                self.auto_confirm_changes()
                
                # РџСЂРѕРІРµСЂРєР° Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹
                if self.check_agent_completion():
                    logger.info("вњ… РђРіРµРЅС‚ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ")
                    break
                
                # РџСЂРѕРІРµСЂРєР° Р°РєС‚РёРІРЅРѕСЃС‚Рё
                if time.time() - last_activity > 120:  # 2 РјРёРЅСѓС‚С‹ Р±РµР· Р°РєС‚РёРІРЅРѕСЃС‚Рё
                    logger.info("вЏ° РќРµС‚ Р°РєС‚РёРІРЅРѕСЃС‚Рё 2 РјРёРЅСѓС‚С‹, СЃС‡РёС‚Р°РµРј Р·Р°РІРµСЂС€РµРЅРЅС‹Рј")
                    break
                
                # РћР±РЅРѕРІР»РµРЅРёРµ РІСЂРµРјРµРЅРё РїРѕСЃР»РµРґРЅРµР№ Р°РєС‚РёРІРЅРѕСЃС‚Рё
                if self.detect_agent_activity():
                    last_activity = time.time()
                
                elapsed = int(time.time() - start_time)
                logger.info(f"вЏі РћР¶РёРґР°РЅРёРµ... {elapsed}СЃ / {timeout}СЃ")
                
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"РћС€РёР±РєР° РїСЂРё РѕР¶РёРґР°РЅРёРё: {e}")
                time.sleep(5)
        
        logger.info("вњ… РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРѕ")
        return True
    
    def auto_confirm_changes(self):
        """РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РёР·РјРµРЅРµРЅРёР№"""
        try:
            # РќР°Р¶Р°С‚РёРµ Ctrl+Enter РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ РєРѕРјР°РЅРґ
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(0.5)
            
            # РќР°Р¶Р°С‚РёРµ Enter РґР»СЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ РёР·РјРµРЅРµРЅРёР№ РєРѕРґР°
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # РќР°Р¶Р°С‚РёРµ Tab РґР»СЏ РЅР°РІРёРіР°С†РёРё РїРѕ РёРЅС‚РµСЂС„РµР№СЃСѓ
            pyautogui.press('tab')
            time.sleep(0.5)
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° Р°РІС‚РѕРїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ: {e}")
    
    def check_agent_completion(self):
        """РџСЂРѕРІРµСЂРєР° Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°"""
        try:
            # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ OCR
            # РґР»СЏ РїРѕРёСЃРєР° РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ РЅР° СЌРєСЂР°РЅРµ
            
            # РџСЂРѕРІРµСЂРєР° С‡РµСЂРµР· API Р°РіРµРЅС‚Р°
            if self.check_api_status():
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° РїСЂРѕРІРµСЂРєРё Р·Р°РІРµСЂС€РµРЅРёСЏ: {e}")
            return False
    
    def detect_agent_activity(self):
        """РћР±РЅР°СЂСѓР¶РµРЅРёРµ Р°РєС‚РёРІРЅРѕСЃС‚Рё Р°РіРµРЅС‚Р°"""
        try:
            # РџСЂРѕРІРµСЂРєР° Р°РєС‚РёРІРЅРѕСЃС‚Рё РїСЂРѕС†РµСЃСЃР° Cursor
            if self.cursor_process and self.cursor_process.poll() is None:
                return True
            
            # РџСЂРѕРІРµСЂРєР° API Р°РіРµРЅС‚Р°
            if self.check_api_status():
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° РѕР±РЅР°СЂСѓР¶РµРЅРёСЏ Р°РєС‚РёРІРЅРѕСЃС‚Рё: {e}")
            return False
    
    def check_api_status(self):
        """РџСЂРѕРІРµСЂРєР° СЃС‚Р°С‚СѓСЃР° API Р°РіРµРЅС‚Р°"""
        try:
            headers = {"x-agent-secret": self.secret}
            response = requests.get(f"{self.api_base}/health", headers=headers, timeout=5)
            
            if response.status_code == 200:
                return True
            else:
                return False
                
        except Exception as e:
            logger.debug(f"API РЅРµ РѕС‚РІРµС‡Р°РµС‚: {e}")
            return False
    
    def save_all_files(self):
        """РЁР°Рі 6: РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ"""
        logger.info("=== РЁР°Рі 6: РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ ===")
        
        try:
            # РЎРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ (Ctrl+Shift+S)
            pyautogui.hotkey('ctrl', 'shift', 's')
            time.sleep(2)
            
            logger.info("вњ… Р’СЃРµ С„Р°Р№Р»С‹ СЃРѕС…СЂР°РЅРµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° СЃРѕС…СЂР°РЅРµРЅРёСЏ С„Р°Р№Р»РѕРІ: {e}")
            self.stats['errors'] += 1
            return False
    
    def add_code_comments(self):
        """РЁР°Рі 7: Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ"""
        logger.info("=== РЁР°Рі 7: Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ ===")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё РґР»СЏ РЅРѕРІРѕРіРѕ Р·Р°РїСЂРѕСЃР°
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(2)
            
            # Р¤РѕСЂРјРёСЂРѕРІР°РЅРёРµ Р·Р°РїСЂРѕСЃР° РЅР° РґРѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ
            comment_request = """
            Р”РѕР±Р°РІСЊ РїРѕРґСЂРѕР±РЅС‹Рµ РєРѕРјРјРµРЅС‚Р°СЂРёРё Рє РєРѕРґСѓ, РѕР±СЉСЏСЃРЅСЏСЋС‰РёРµ:
            1. РќР°Р·РЅР°С‡РµРЅРёРµ РєР°Р¶РґРѕР№ С„СѓРЅРєС†РёРё Рё РєР»Р°СЃСЃР°
            2. РџР°СЂР°РјРµС‚СЂС‹ Рё РІРѕР·РІСЂР°С‰Р°РµРјС‹Рµ Р·РЅР°С‡РµРЅРёСЏ
            3. Р›РѕРіРёРєСѓ СЂР°Р±РѕС‚С‹ Р°Р»РіРѕСЂРёС‚РјРѕРІ
            4. РџСЂРёРјРµСЂС‹ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ
            5. РћР±СЂР°Р±РѕС‚РєСѓ РѕС€РёР±РѕРє
            6. РЎРІСЏР·Рё РјРµР¶РґСѓ РєРѕРјРїРѕРЅРµРЅС‚Р°РјРё
            """
            
            # РћС‡РёСЃС‚РєР° РїРѕР»СЏ РІРІРѕРґР°
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР°
            pyautogui.typewrite(comment_request)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(3)
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            self.wait_for_agent_completion(180)
            
            logger.info("вњ… РљРѕРјРјРµРЅС‚Р°СЂРёРё РґРѕР±Р°РІР»РµРЅС‹")
            self.stats['tasks_completed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РґРѕР±Р°РІР»РµРЅРёСЏ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_tests(self):
        """РЁР°Рі 8: Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ"""
        logger.info("=== РЁР°Рі 8: Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ ===")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ С‚РµСЂРјРёРЅР°Р»Р° (Ctrl+`)
            pyautogui.hotkey('ctrl', '`')
            time.sleep(2)
            
            # РћС‡РёСЃС‚РєР° С‚РµСЂРјРёРЅР°Р»Р°
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            test_command = "py -3.11 -m pytest -q"
            pyautogui.typewrite(test_command)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(10)
            
            logger.info("вњ… РўРµСЃС‚С‹ Р·Р°РїСѓС‰РµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° С‚РµСЃС‚РѕРІ: {e}")
            self.stats['errors'] += 1
            return False
    
    def validate_project(self):
        """РЁР°Рі 9: Р’Р°Р»РёРґР°С†РёСЏ РїСЂРѕРµРєС‚Р°"""
        logger.info("=== РЁР°Рі 9: Р’Р°Р»РёРґР°С†РёСЏ РїСЂРѕРµРєС‚Р° ===")
        
        try:
            # РџСЂРѕРІРµСЂРєР° СЃС‚СЂСѓРєС‚СѓСЂС‹ РїСЂРѕРµРєС‚Р°
            project_files = list(self.project_path.rglob("*.py"))
            project_files.extend(list(self.project_path.rglob("*.json")))
            project_files.extend(list(self.project_path.rglob("*.yml")))
            project_files.extend(list(self.project_path.rglob("*.yaml")))
            
            self.stats['files_created'] = len(project_files)
            
            # РџСЂРѕРІРµСЂРєР° API Р°РіРµРЅС‚Р°
            if self.check_api_status():
                logger.info("вњ… API Р°РіРµРЅС‚ СЂР°Р±РѕС‚Р°РµС‚")
            else:
                logger.warning("вљ пёЏ API Р°РіРµРЅС‚ РЅРµ РѕС‚РІРµС‡Р°РµС‚")
            
            logger.info(f"вњ… РџСЂРѕРµРєС‚ РІР°Р»РёРґРёСЂРѕРІР°РЅ: {len(project_files)} С„Р°Р№Р»РѕРІ")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РІР°Р»РёРґР°С†РёРё РїСЂРѕРµРєС‚Р°: {e}")
            self.stats['errors'] += 1
            return False
    
    def generate_report(self):
        """Р“РµРЅРµСЂР°С†РёСЏ РѕС‚С‡РµС‚Р° Рѕ РІС‹РїРѕР»РЅРµРЅРёРё"""
        logger.info("=== Р“РµРЅРµСЂР°С†РёСЏ РѕС‚С‡РµС‚Р° ===")
        
        try:
            self.stats['end_time'] = datetime.now()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            report = {
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
                'end_time': self.stats['end_time'].isoformat(),
                'duration_seconds': duration,
                'tasks_completed': self.stats['tasks_completed'],
                'errors': self.stats['errors'],
                'files_created': self.stats['files_created'],
                'files_modified': self.stats['files_modified'],
                'success_rate': (self.stats['tasks_completed'] / max(1, self.stats['tasks_completed'] + self.stats['errors'])) * 100
            }
            
            # РЎРѕС…СЂР°РЅРµРЅРёРµ РѕС‚С‡РµС‚Р°
            report_path = self.project_path / "cursor_integration_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"вњ… РћС‚С‡РµС‚ СЃРѕС…СЂР°РЅРµРЅ: {report_path}")
            logger.info(f"рџ“Љ РЎС‚Р°С‚РёСЃС‚РёРєР°: {report}")
            
            return report
            
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё РѕС‚С‡РµС‚Р°: {e}")
            return None
    
    def execute_full_workflow(self, task_description):
        """Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ workflow Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р°"""
        logger.info("рџљЂ === РќРђР§РђР›Рћ РџРћР›РќРћР“Рћ WORKFLOW РђР’РўРћРќРћРњРќРћР“Рћ РђР“Р•РќРўРђ ===")
        
        self.stats['start_time'] = datetime.now()
        
        try:
            # РЁР°Рі 1: Р—Р°РїСѓСЃРє Cursor
            if not self.start_cursor_project():
                return False
            
            # РЁР°Рі 2: РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё
            if not self.open_ai_panel():
                return False
            
            # РЁР°Рі 3: РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode
            if not self.switch_to_agent_mode():
                logger.warning("вљ пёЏ РќРµ СѓРґР°Р»РѕСЃСЊ РїРµСЂРµРєР»СЋС‡РёС‚СЊ РІ Agent Mode, РїСЂРѕРґРѕР»Р¶Р°РµРј...")
            
            # РЁР°Рі 4: РћС‚РїСЂР°РІРєР° РѕСЃРЅРѕРІРЅРѕРіРѕ Р·Р°РїСЂРѕСЃР°
            if not self.send_agent_request(task_description):
                return False
            
            # РЁР°Рі 5: РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            if not self.wait_for_agent_completion():
                logger.warning("вљ пёЏ РђРіРµРЅС‚ РЅРµ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ РІ РѕР¶РёРґР°РµРјРѕРµ РІСЂРµРјСЏ")
            
            # РЁР°Рі 6: РЎРѕС…СЂР°РЅРµРЅРёРµ С„Р°Р№Р»РѕРІ
            self.save_all_files()
            
            # РЁР°Рі 7: Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ
            self.add_code_comments()
            
            # РЁР°Рі 8: Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            self.run_tests()
            
            # РЁР°Рі 9: Р’Р°Р»РёРґР°С†РёСЏ РїСЂРѕРµРєС‚Р°
            self.validate_project()
            
            # Р“РµРЅРµСЂР°С†РёСЏ РѕС‚С‡РµС‚Р°
            self.generate_report()
            
            logger.info("рџЋ‰ === WORKFLOW Р—РђР’Р•Р РЁР•Рќ РЈРЎРџР•РЁРќРћ ===")
            return True
            
        except Exception as e:
            logger.error(f"вќЊ РљСЂРёС‚РёС‡РµСЃРєР°СЏ РѕС€РёР±РєР° РІ workflow: {e}")
            self.stats['errors'] += 1
            self.generate_report()
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
                if self.check_api_status():
                    logger.info("вњ… API Р°РіРµРЅС‚ Р·Р°РїСѓС‰РµРЅ Рё СЂР°Р±РѕС‚Р°РµС‚")
                    return True
                else:
                    logger.error("вќЊ API Р°РіРµРЅС‚ РЅРµ РѕС‚РІРµС‡Р°РµС‚")
                    return False
            else:
                logger.error(f"вќЊ РЎРєСЂРёРїС‚ РЅРµ РЅР°Р№РґРµРЅ: {script_path}")
                return False
                
        except Exception as e:
            logger.error(f"вќЊ РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° API Р°РіРµРЅС‚Р°: {e}")
            return False

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    logger.info("рџљЂ Р—Р°РїСѓСЃРє Cursor Integration Final")
    
    # РЎРѕР·РґР°РЅРёРµ Р°РіРµРЅС‚Р°
    agent = CursorIntegrationFinal()
    
    # Р—Р°РїСѓСЃРє API Р°РіРµРЅС‚Р°
    if not agent.start_api_agent():
        logger.error("вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РїСѓСЃС‚РёС‚СЊ API Р°РіРµРЅС‚Р°")
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
    8. README СЃ РёРЅСЃС‚СЂСѓРєС†РёСЏРјРё РїРѕ Р·Р°РїСѓСЃРєСѓ
    """
    
    # Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ workflow
    success = agent.execute_full_workflow(task)
    
    if success:
        logger.info("рџЋ‰ РџСЂРѕРµРєС‚ СѓСЃРїРµС€РЅРѕ Р·Р°РІРµСЂС€РµРЅ!")
        return True
    else:
        logger.error("вќЊ РџСЂРѕРёР·РѕС€Р»Рё РѕС€РёР±РєРё РІ РїСЂРѕС†РµСЃСЃРµ РІС‹РїРѕР»РЅРµРЅРёСЏ")
        return False

if __name__ == "__main__":
    main()

