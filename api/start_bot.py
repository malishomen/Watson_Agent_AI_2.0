#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
РџСЂРѕСЃС‚РѕР№ Р·Р°РїСѓСЃРє Telegram Р±РѕС‚Р° РґР»СЏ Windows
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Р”РѕР±Р°РІР»СЏРµРј РєРѕСЂРЅРµРІСѓСЋ РґРёСЂРµРєС‚РѕСЂРёСЋ РІ РїСѓС‚СЊ
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# РќР°СЃС‚СЂР°РёРІР°РµРј РїРµСЂРµРјРµРЅРЅС‹Рµ РѕРєСЂСѓР¶РµРЅРёСЏ
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "7073794782:AAHgCryXTUXZ0TOvQ7_xZaccTBp_uwm0gvk")
os.environ.setdefault("TELEGRAM_ALLOWED_USER_IDS", "73332538")
os.environ.setdefault("TELEGRAM_ADMIN_USER_ID", "73332538")
os.environ.setdefault("AGENT_HTTP_SHARED_SECRET", "change_me_long_random")

# РРјРїРѕСЂС‚РёСЂСѓРµРј Рё Р·Р°РїСѓСЃРєР°РµРј Р±РѕС‚Р°
try:
    from bot.telegram_operator import main
    
    logging.basicConfig(level=logging.INFO)
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    print("Р—Р°РїСѓСЃРє Telegram Р±РѕС‚Р°...")
    asyncio.run(main())
    
except KeyboardInterrupt:
    print("Р‘РѕС‚ РѕСЃС‚Р°РЅРѕРІР»РµРЅ")
except Exception as e:
    print(f"РћС€РёР±РєР°: {e}")
    sys.exit(1)
