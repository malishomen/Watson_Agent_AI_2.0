#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Cursor Automation Agent
РџСЂРѕРґРІРёРЅСѓС‚С‹Р№ Р°РІС‚РѕРЅРѕРјРЅС‹Р№ Р°РіРµРЅС‚ РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ Cursor СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј pyautogui
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
import cv2
import numpy as np
from PIL import Image
import logging
import threading
import queue

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cursor_automation_advanced.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedCursorAutomationAgent:
    """РџСЂРѕРґРІРёРЅСѓС‚С‹Р№ Р°РІС‚РѕРЅРѕРјРЅС‹Р№ Р°РіРµРЅС‚ РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ Cursor"""
    
    def __init__(self, project_path="D:/AI-Agent", secret="test123"):
        self.project_path = Path(project_path)
        self.secret = secret
        self.api_base = "http://127.0.0.1:8088"
        self.cursor_process = None
        self.screenshot_queue = queue.Queue()
        self.monitoring_active = False
        
        # РќР°СЃС‚СЂРѕР№РєР° pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        # РќР°СЃС‚СЂРѕР№РєР° СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ РёР·РѕР±СЂР°Р¶РµРЅРёР№
        self.template_path = Path("templates")
        self.template_path.mkdir(exist_ok=True)
        
        logger.info(f"РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїСЂРѕРґРІРёРЅСѓС‚РѕРіРѕ Р°РіРµРЅС‚Р° РґР»СЏ РїСЂРѕРµРєС‚Р°: {self.project_path}")
    
    def start_cursor_with_monitoring(self):
        """Р—Р°РїСѓСЃРє Cursor СЃ РјРѕРЅРёС‚РѕСЂРёРЅРіРѕРј СЌРєСЂР°РЅР°"""
        logger.info("Р—Р°РїСѓСЃРє Cursor СЃ РјРѕРЅРёС‚РѕСЂРёРЅРіРѕРј...")
        
        try:
            # Р—Р°РїСѓСЃРє Cursor
            self.cursor_process = subprocess.Popen([
                "cursor", str(self.project_path)
            ], shell=True)
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РіСЂСѓР·РєРё
            time.sleep(8)
            
            # Р—Р°РїСѓСЃРє РјРѕРЅРёС‚РѕСЂРёРЅРіР° СЌРєСЂР°РЅР°
            self.start_screen_monitoring()
            
            logger.info("Cursor Р·Р°РїСѓС‰РµРЅ СЃ РјРѕРЅРёС‚РѕСЂРёРЅРіРѕРј")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° Cursor: {e}")
            return False
    
    def start_screen_monitoring(self):
        """Р—Р°РїСѓСЃРє РјРѕРЅРёС‚РѕСЂРёРЅРіР° СЌРєСЂР°РЅР° РґР»СЏ РѕС‚СЃР»РµР¶РёРІР°РЅРёСЏ СЃРѕСЃС‚РѕСЏРЅРёСЏ Cursor"""
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._screen_monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("РњРѕРЅРёС‚РѕСЂРёРЅРі СЌРєСЂР°РЅР° Р·Р°РїСѓС‰РµРЅ")
    
    def _screen_monitor_loop(self):
        """Р¦РёРєР» РјРѕРЅРёС‚РѕСЂРёРЅРіР° СЌРєСЂР°РЅР°"""
        while self.monitoring_active:
            try:
                # РЎРѕР·РґР°РЅРёРµ СЃРєСЂРёРЅС€РѕС‚Р°
                screenshot = pyautogui.screenshot()
                
                # РђРЅР°Р»РёР· СЃРѕСЃС‚РѕСЏРЅРёСЏ Cursor
                self._analyze_cursor_state(screenshot)
                
                time.sleep(2)  # РџСЂРѕРІРµСЂРєР° РєР°Р¶РґС‹Рµ 2 СЃРµРєСѓРЅРґС‹
                
            except Exception as e:
                logger.debug(f"РћС€РёР±РєР° РјРѕРЅРёС‚РѕСЂРёРЅРіР°: {e}")
                time.sleep(1)
    
    def _analyze_cursor_state(self, screenshot):
        """РђРЅР°Р»РёР· СЃРѕСЃС‚РѕСЏРЅРёСЏ Cursor РїРѕ СЃРєСЂРёРЅС€РѕС‚Сѓ"""
        try:
            # РљРѕРЅРІРµСЂС‚Р°С†РёСЏ РІ numpy array РґР»СЏ OpenCV
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # РџРѕРёСЃРє РёРЅРґРёРєР°С‚РѕСЂРѕРІ СЃРѕСЃС‚РѕСЏРЅРёСЏ
            self._detect_ai_panel(img)
            self._detect_agent_mode(img)
            self._detect_completion_indicators(img)
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° Р°РЅР°Р»РёР·Р° СЃРѕСЃС‚РѕСЏРЅРёСЏ: {e}")
    
    def _detect_ai_panel(self, img):
        """РћР±РЅР°СЂСѓР¶РµРЅРёРµ AI-РїР°РЅРµР»Рё"""
        # РџРѕРёСЃРє С…Р°СЂР°РєС‚РµСЂРЅС‹С… СЌР»РµРјРµРЅС‚РѕРІ AI-РїР°РЅРµР»Рё
        # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ С€Р°Р±Р»РѕРЅС‹
        pass
    
    def _detect_agent_mode(self, img):
        """РћР±РЅР°СЂСѓР¶РµРЅРёРµ Agent Mode"""
        # РџРѕРёСЃРє РёРЅРґРёРєР°С‚РѕСЂРѕРІ Agent Mode
        pass
    
    def _detect_completion_indicators(self, img):
        """РћР±РЅР°СЂСѓР¶РµРЅРёРµ РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹"""
        # РџРѕРёСЃРє С‚РµРєСЃС‚Р° "Task completed", "Done", etc.
        pass
    
    def smart_click(self, x, y, confidence=0.8):
        """РЈРјРЅС‹Р№ РєР»РёРє СЃ РїСЂРѕРІРµСЂРєРѕР№"""
        try:
            # РџСЂРѕРІРµСЂРєР°, С‡С‚Рѕ РєРѕРѕСЂРґРёРЅР°С‚С‹ РІ РїСЂРµРґРµР»Р°С… СЌРєСЂР°РЅР°
            screen_width, screen_height = pyautogui.size()
            if 0 <= x <= screen_width and 0 <= y <= screen_height:
                pyautogui.click(x, y)
                time.sleep(0.5)
                return True
            else:
                logger.warning(f"РљРѕРѕСЂРґРёРЅР°С‚С‹ РІРЅРµ СЌРєСЂР°РЅР°: ({x}, {y})")
                return False
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РєР»РёРєР°: {e}")
            return False
    
    def smart_type(self, text, delay=0.1):
        """РЈРјРЅС‹Р№ РІРІРѕРґ С‚РµРєСЃС‚Р° СЃ Р·Р°РґРµСЂР¶РєР°РјРё"""
        try:
            for char in text:
                pyautogui.typewrite(char)
                time.sleep(delay)
            return True
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РІРІРѕРґР° С‚РµРєСЃС‚Р°: {e}")
            return False
    
    def find_and_click_template(self, template_name, confidence=0.8):
        """РџРѕРёСЃРє Рё РєР»РёРє РїРѕ С€Р°Р±Р»РѕРЅСѓ"""
        try:
            template_path = self.template_path / f"{template_name}.png"
            
            if not template_path.exists():
                logger.warning(f"РЁР°Р±Р»РѕРЅ РЅРµ РЅР°Р№РґРµРЅ: {template_path}")
                return False
            
            # РџРѕРёСЃРє С€Р°Р±Р»РѕРЅР° РЅР° СЌРєСЂР°РЅРµ
            location = pyautogui.locateOnScreen(str(template_path), confidence=confidence)
            
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                logger.info(f"РќР°Р№РґРµРЅ Рё РєР»РёРєРЅСѓС‚ С€Р°Р±Р»РѕРЅ: {template_name}")
                return True
            else:
                logger.debug(f"РЁР°Р±Р»РѕРЅ РЅРµ РЅР°Р№РґРµРЅ: {template_name}")
                return False
                
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РїРѕРёСЃРєР° С€Р°Р±Р»РѕРЅР° {template_name}: {e}")
            return False
    
    def open_ai_panel_smart(self):
        """РЈРјРЅРѕРµ РѕС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё"""
        logger.info("РЈРјРЅРѕРµ РѕС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё...")
        
        try:
            # РџРѕРїС‹С‚РєР° РЅР°Р№С‚Рё РєРЅРѕРїРєСѓ AI-РїР°РЅРµР»Рё
            if self.find_and_click_template("ai_panel_button"):
                time.sleep(2)
                return True
            
            # Р•СЃР»Рё РЅРµ РЅР°Р№РґРµРЅР°, РёСЃРїРѕР»СЊР·СѓРµРј РіРѕСЂСЏС‡РёРµ РєР»Р°РІРёС€Рё
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(2)
            
            # РџСЂРѕРІРµСЂРєР° СѓСЃРїРµС€РЅРѕСЃС‚Рё РѕС‚РєСЂС‹С‚РёСЏ
            if self.find_and_click_template("ai_panel_open"):
                logger.info("AI-РїР°РЅРµР»СЊ РѕС‚РєСЂС‹С‚Р°")
                return True
            else:
                logger.warning("РќРµ СѓРґР°Р»РѕСЃСЊ РїРѕРґС‚РІРµСЂРґРёС‚СЊ РѕС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё")
                return False
                
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РѕС‚РєСЂС‹С‚РёСЏ AI-РїР°РЅРµР»Рё: {e}")
            return False
    
    def switch_to_agent_mode_smart(self):
        """РЈРјРЅРѕРµ РїРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode"""
        logger.info("РЈРјРЅРѕРµ РїРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode...")
        
        try:
            # РџРѕРёСЃРє РїРµСЂРµРєР»СЋС‡Р°С‚РµР»СЏ Agent Mode
            if self.find_and_click_template("agent_mode_toggle"):
                time.sleep(2)
                return True
            
            # РђР»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Р№ СЃРїРѕСЃРѕР± С‡РµСЂРµР· РєРѕРјР°РЅРґРЅСѓСЋ РїР°Р»РёС‚СЂСѓ
            pyautogui.hotkey('ctrl', 'shift', 'p')
            time.sleep(1)
            
            # Р’РІРѕРґ РєРѕРјР°РЅРґС‹
            self.smart_type("Enable Agent Mode")
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # РџСЂРѕРІРµСЂРєР° СѓСЃРїРµС€РЅРѕСЃС‚Рё
            if self.find_and_click_template("agent_mode_active"):
                logger.info("Agent Mode Р°РєС‚РёРІРёСЂРѕРІР°РЅ")
                return True
            else:
                logger.warning("РќРµ СѓРґР°Р»РѕСЃСЊ РїРѕРґС‚РІРµСЂРґРёС‚СЊ Р°РєС‚РёРІР°С†РёСЋ Agent Mode")
                return False
                
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РїРµСЂРµРєР»СЋС‡РµРЅРёСЏ РІ Agent Mode: {e}")
            return False
    
    def send_agent_request_smart(self, task_description):
        """РЈРјРЅР°СЏ РѕС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ"""
        logger.info(f"РЈРјРЅР°СЏ РѕС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР° Р°РіРµРЅС‚Сѓ: {task_description[:50]}...")
        
        try:
            # РџРѕРёСЃРє РїРѕР»СЏ РІРІРѕРґР°
            if self.find_and_click_template("input_field"):
                time.sleep(1)
            else:
                # Р•СЃР»Рё РЅРµ РЅР°Р№РґРµРЅРѕ, РїРѕРїСЂРѕР±СѓРµРј РєР»РёРєРЅСѓС‚СЊ РІ С†РµРЅС‚СЂ СЌРєСЂР°РЅР°
                screen_width, screen_height = pyautogui.size()
                pyautogui.click(screen_width // 2, screen_height // 2)
                time.sleep(1)
            
            # РћС‡РёСЃС‚РєР° РїРѕР»СЏ РІРІРѕРґР°
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # Р’РІРѕРґ С‚РµРєСЃС‚Р° Р·Р°РґР°С‡Рё
            self.smart_type(task_description, delay=0.05)
            time.sleep(1)
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР°
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("Р—Р°РїСЂРѕСЃ РѕС‚РїСЂР°РІР»РµРЅ Р°РіРµРЅС‚Сѓ")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РѕС‚РїСЂР°РІРєРё Р·Р°РїСЂРѕСЃР°: {e}")
            return False
    
    def wait_for_agent_completion_smart(self, timeout=600):
        """РЈРјРЅРѕРµ РѕР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°"""
        logger.info("РЈРјРЅРѕРµ РѕР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ СЂР°Р±РѕС‚С‹ Р°РіРµРЅС‚Р°...")
        
        start_time = time.time()
        last_activity = start_time
        
        while time.time() - start_time < timeout:
            try:
                # РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ РёР·РјРµРЅРµРЅРёР№
                self.auto_confirm_smart()
                
                # РџСЂРѕРІРµСЂРєР° РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ
                if self.check_completion_indicators():
                    logger.info("РћР±РЅР°СЂСѓР¶РµРЅС‹ РёРЅРґРёРєР°С‚РѕСЂС‹ Р·Р°РІРµСЂС€РµРЅРёСЏ")
                    break
                
                # РџСЂРѕРІРµСЂРєР° Р°РєС‚РёРІРЅРѕСЃС‚Рё (РµСЃР»Рё РЅРµС‚ Р°РєС‚РёРІРЅРѕСЃС‚Рё 2 РјРёРЅСѓС‚С‹, СЃС‡РёС‚Р°РµРј Р·Р°РІРµСЂС€РµРЅРЅС‹Рј)
                if time.time() - last_activity > 120:
                    logger.info("РќРµС‚ Р°РєС‚РёРІРЅРѕСЃС‚Рё 2 РјРёРЅСѓС‚С‹, СЃС‡РёС‚Р°РµРј Р·Р°РІРµСЂС€РµРЅРЅС‹Рј")
                    break
                
                # РћР±РЅРѕРІР»РµРЅРёРµ РІСЂРµРјРµРЅРё РїРѕСЃР»РµРґРЅРµР№ Р°РєС‚РёРІРЅРѕСЃС‚Рё
                if self.detect_activity():
                    last_activity = time.time()
                
                time.sleep(5)
                
                elapsed = int(time.time() - start_time)
                logger.info(f"РћР¶РёРґР°РЅРёРµ... {elapsed}СЃ / {timeout}СЃ")
                
            except Exception as e:
                logger.error(f"РћС€РёР±РєР° РїСЂРё РѕР¶РёРґР°РЅРёРё: {e}")
                time.sleep(5)
        
        logger.info("РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРѕ")
        return True
    
    def auto_confirm_smart(self):
        """РЈРјРЅРѕРµ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРѕРµ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ"""
        try:
            # РџРѕРёСЃРє РєРЅРѕРїРѕРє РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ
            if self.find_and_click_template("confirm_button"):
                time.sleep(1)
                return True
            
            # РђР»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Рµ СЃРїРѕСЃРѕР±С‹ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° Р°РІС‚РѕРїРѕРґС‚РІРµСЂР¶РґРµРЅРёСЏ: {e}")
    
    def check_completion_indicators(self):
        """РџСЂРѕРІРµСЂРєР° РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ"""
        try:
            # РџРѕРёСЃРє С‚РµРєСЃС‚РѕРІС‹С… РёРЅРґРёРєР°С‚РѕСЂРѕРІ Р·Р°РІРµСЂС€РµРЅРёСЏ
            completion_indicators = [
                "Task completed",
                "Done",
                "Finished",
                "Complete",
                "вњ…",
                "Р“РѕС‚РѕРІРѕ"
            ]
            
            # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ OCR
            # РґР»СЏ РїРѕРёСЃРєР° СЌС‚РёС… РёРЅРґРёРєР°С‚РѕСЂРѕРІ РЅР° СЌРєСЂР°РЅРµ
            
            return False  # Р—Р°РіР»СѓС€РєР°
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° РїСЂРѕРІРµСЂРєРё Р·Р°РІРµСЂС€РµРЅРёСЏ: {e}")
            return False
    
    def detect_activity(self):
        """РћР±РЅР°СЂСѓР¶РµРЅРёРµ Р°РєС‚РёРІРЅРѕСЃС‚Рё Р°РіРµРЅС‚Р°"""
        try:
            # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ РјРѕР¶РЅРѕ Р°РЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ РёР·РјРµРЅРµРЅРёСЏ РЅР° СЌРєСЂР°РЅРµ
            # РёР»Рё РѕС‚СЃР»РµР¶РёРІР°С‚СЊ Р°РєС‚РёРІРЅРѕСЃС‚СЊ РїСЂРѕС†РµСЃСЃР° Cursor
            
            return True  # Р—Р°РіР»СѓС€РєР°
            
        except Exception as e:
            logger.debug(f"РћС€РёР±РєР° РѕР±РЅР°СЂСѓР¶РµРЅРёСЏ Р°РєС‚РёРІРЅРѕСЃС‚Рё: {e}")
            return False
    
    def save_all_files_smart(self):
        """РЈРјРЅРѕРµ СЃРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ"""
        logger.info("РЈРјРЅРѕРµ СЃРѕС…СЂР°РЅРµРЅРёРµ РІСЃРµС… С„Р°Р№Р»РѕРІ...")
        
        try:
            # РџРѕРёСЃРє РєРЅРѕРїРєРё СЃРѕС…СЂР°РЅРµРЅРёСЏ
            if self.find_and_click_template("save_button"):
                time.sleep(1)
                return True
            
            # РђР»СЊС‚РµСЂРЅР°С‚РёРІРЅС‹Р№ СЃРїРѕСЃРѕР±
            pyautogui.hotkey('ctrl', 'shift', 's')
            time.sleep(1)
            
            logger.info("Р’СЃРµ С„Р°Р№Р»С‹ СЃРѕС…СЂР°РЅРµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° СЃРѕС…СЂР°РЅРµРЅРёСЏ С„Р°Р№Р»РѕРІ: {e}")
            return False
    
    def add_code_comments_smart(self):
        """РЈРјРЅРѕРµ РґРѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ"""
        logger.info("РЈРјРЅРѕРµ РґРѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ Рє РєРѕРґСѓ...")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё
            if not self.open_ai_panel_smart():
                return False
            
            # Р¤РѕСЂРјРёСЂРѕРІР°РЅРёРµ Р·Р°РїСЂРѕСЃР°
            comment_request = """
            Р”РѕР±Р°РІСЊ РїРѕРґСЂРѕР±РЅС‹Рµ РєРѕРјРјРµРЅС‚Р°СЂРёРё Рє РєРѕРґСѓ, РѕР±СЉСЏСЃРЅСЏСЋС‰РёРµ:
            1. РќР°Р·РЅР°С‡РµРЅРёРµ РєР°Р¶РґРѕР№ С„СѓРЅРєС†РёРё
            2. РџР°СЂР°РјРµС‚СЂС‹ Рё РІРѕР·РІСЂР°С‰Р°РµРјС‹Рµ Р·РЅР°С‡РµРЅРёСЏ
            3. Р›РѕРіРёРєСѓ СЂР°Р±РѕС‚С‹ Р°Р»РіРѕСЂРёС‚РјРѕРІ
            4. РџСЂРёРјРµСЂС‹ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ
            5. РћР±СЂР°Р±РѕС‚РєСѓ РѕС€РёР±РѕРє
            """
            
            # РћС‚РїСЂР°РІРєР° Р·Р°РїСЂРѕСЃР°
            if not self.send_agent_request_smart(comment_request):
                return False
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            self.wait_for_agent_completion_smart(180)
            
            logger.info("РљРѕРјРјРµРЅС‚Р°СЂРёРё РґРѕР±Р°РІР»РµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РґРѕР±Р°РІР»РµРЅРёСЏ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ: {e}")
            return False
    
    def run_tests_smart(self):
        """РЈРјРЅС‹Р№ Р·Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ"""
        logger.info("РЈРјРЅС‹Р№ Р·Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ...")
        
        try:
            # РћС‚РєСЂС‹С‚РёРµ С‚РµСЂРјРёРЅР°Р»Р°
            pyautogui.hotkey('ctrl', '`')
            time.sleep(2)
            
            # РћС‡РёСЃС‚РєР° С‚РµСЂРјРёРЅР°Р»Р°
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            test_command = "py -3.11 -m pytest -q"
            self.smart_type(test_command)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(5)
            
            logger.info("РўРµСЃС‚С‹ Р·Р°РїСѓС‰РµРЅС‹")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР° С‚РµСЃС‚РѕРІ: {e}")
            return False
    
    def execute_full_workflow_smart(self, task_description):
        """Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ СѓРјРЅРѕРіРѕ workflow"""
        logger.info("=== РќР°С‡Р°Р»Рѕ РїРѕР»РЅРѕРіРѕ СѓРјРЅРѕРіРѕ workflow ===")
        
        try:
            # Р—Р°РїСѓСЃРє Cursor СЃ РјРѕРЅРёС‚РѕСЂРёРЅРіРѕРј
            if not self.start_cursor_with_monitoring():
                return False
            
            # РћС‚РєСЂС‹С‚РёРµ AI-РїР°РЅРµР»Рё
            if not self.open_ai_panel_smart():
                return False
            
            # РџРµСЂРµРєР»СЋС‡РµРЅРёРµ РІ Agent Mode
            if not self.switch_to_agent_mode_smart():
                logger.warning("РќРµ СѓРґР°Р»РѕСЃСЊ РїРµСЂРµРєР»СЋС‡РёС‚СЊ РІ Agent Mode, РїСЂРѕРґРѕР»Р¶Р°РµРј...")
            
            # РћС‚РїСЂР°РІРєР° РѕСЃРЅРѕРІРЅРѕРіРѕ Р·Р°РїСЂРѕСЃР°
            if not self.send_agent_request_smart(task_description):
                return False
            
            # РћР¶РёРґР°РЅРёРµ Р·Р°РІРµСЂС€РµРЅРёСЏ
            if not self.wait_for_agent_completion_smart():
                logger.warning("РђРіРµРЅС‚ РЅРµ Р·Р°РІРµСЂС€РёР» СЂР°Р±РѕС‚Сѓ РІ РѕР¶РёРґР°РµРјРѕРµ РІСЂРµРјСЏ")
            
            # РЎРѕС…СЂР°РЅРµРЅРёРµ С„Р°Р№Р»РѕРІ
            self.save_all_files_smart()
            
            # Р”РѕР±Р°РІР»РµРЅРёРµ РєРѕРјРјРµРЅС‚Р°СЂРёРµРІ
            self.add_code_comments_smart()
            
            # Р—Р°РїСѓСЃРє С‚РµСЃС‚РѕРІ
            self.run_tests_smart()
            
            # РћСЃС‚Р°РЅРѕРІРєР° РјРѕРЅРёС‚РѕСЂРёРЅРіР°
            self.monitoring_active = False
            
            logger.info("=== РЈРјРЅС‹Р№ workflow Р·Р°РІРµСЂС€РµРЅ СѓСЃРїРµС€РЅРѕ ===")
            return True
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° РІ СѓРјРЅРѕРј workflow: {e}")
            self.monitoring_active = False
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
    logger.info("Р—Р°РїСѓСЃРє Advanced Cursor Automation Agent")
    
    # РЎРѕР·РґР°РЅРёРµ Р°РіРµРЅС‚Р°
    agent = AdvancedCursorAutomationAgent()
    
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
    
    # Р’С‹РїРѕР»РЅРµРЅРёРµ РїРѕР»РЅРѕРіРѕ СѓРјРЅРѕРіРѕ workflow
    success = agent.execute_full_workflow_smart(task)
    
    if success:
        logger.info("РџСЂРѕРµРєС‚ СѓСЃРїРµС€РЅРѕ Р·Р°РІРµСЂС€РµРЅ!")
    else:
        logger.error("РџСЂРѕРёР·РѕС€Р»Рё РѕС€РёР±РєРё РІ РїСЂРѕС†РµСЃСЃРµ РІС‹РїРѕР»РЅРµРЅРёСЏ")
    
    return success

if __name__ == "__main__":
    main()

