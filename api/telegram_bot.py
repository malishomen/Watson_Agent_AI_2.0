# Telegram Bot РґР»СЏ AI Agent + Cursor Automation
# РРЅС‚РµРіСЂР°С†РёСЏ СЃ API Р°РіРµРЅС‚РѕРј Рё Р°РІС‚РѕРјР°С‚РёР·Р°С†РёСЏ Cursor

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import os
from typing import Dict, Any

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ
API_BASE_URL = "http://127.0.0.1:8088"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USERS = [int(x) for x in os.getenv("ALLOWED_USERS", "123456789").split(",")]

class AIAgentBot:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.allowed_users = ALLOWED_USERS
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РљРѕРјР°РЅРґР° /start"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("вќЊ Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ")
            return
            
        await update.message.reply_text(
            "рџ¤– **AI Agent + Cursor Automation Bot**\n\n"
            "Р”РѕСЃС‚СѓРїРЅС‹Рµ РєРѕРјР°РЅРґС‹:\n"
            "/start - РќР°С‡Р°С‚СЊ СЂР°Р±РѕС‚Сѓ\n"
            "/status - РЎС‚Р°С‚СѓСЃ СЃРёСЃС‚РµРјС‹\n"
            "/task <РѕРїРёСЃР°РЅРёРµ> - РЎРѕР·РґР°С‚СЊ Р·Р°РґР°С‡Сѓ\n"
            "/help - РџРѕРјРѕС‰СЊ\n\n"
            "РџСЂРѕСЃС‚Рѕ РѕС‚РїСЂР°РІСЊС‚Рµ РѕРїРёСЃР°РЅРёРµ Р·Р°РґР°С‡Рё, Рё СЏ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РІС‹РїРѕР»РЅСЋ РµС‘ РІ Cursor!"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РљРѕРјР°РЅРґР° /help"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("вќЊ Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ")
            return
            
        await update.message.reply_text(
            "рџ“‹ **РџРѕРјРѕС‰СЊ РїРѕ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЋ Р±РѕС‚Р°**\n\n"
            "**РћСЃРЅРѕРІРЅС‹Рµ РєРѕРјР°РЅРґС‹:**\n"
            "вЂў `/start` - РќР°С‡Р°С‚СЊ СЂР°Р±РѕС‚Сѓ СЃ Р±РѕС‚РѕРј\n"
            "вЂў `/status` - РџСЂРѕРІРµСЂРёС‚СЊ СЃС‚Р°С‚СѓСЃ СЃРёСЃС‚РµРјС‹\n"
            "вЂў `/task <РѕРїРёСЃР°РЅРёРµ>` - РЎРѕР·РґР°С‚СЊ РЅРѕРІСѓСЋ Р·Р°РґР°С‡Сѓ\n"
            "вЂў `/help` - РџРѕРєР°Р·Р°С‚СЊ СЌС‚Сѓ СЃРїСЂР°РІРєСѓ\n\n"
            "**РџСЂРёРјРµСЂС‹ Р·Р°РґР°С‡:**\n"
            "вЂў `РЎРѕР·РґР°С‚СЊ REST API РЅР° FastAPI`\n"
            "вЂў `Р”РѕР±Р°РІРёС‚СЊ Р°СѓС‚РµРЅС‚РёС„РёРєР°С†РёСЋ РІ РїСЂРѕРµРєС‚`\n"
            "вЂў `РЎРѕР·РґР°С‚СЊ РІРµР±-РёРЅС‚РµСЂС„РµР№СЃ РґР»СЏ СѓРїСЂР°РІР»РµРЅРёСЏ`\n\n"
            "РџСЂРѕСЃС‚Рѕ РѕС‚РїСЂР°РІСЊС‚Рµ РѕРїРёСЃР°РЅРёРµ Р·Р°РґР°С‡Рё С‚РµРєСЃС‚РѕРј!"
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РљРѕРјР°РЅРґР° /status"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("вќЊ Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ")
            return
            
        try:
            # РџСЂРѕРІРµСЂРєР° API Р°РіРµРЅС‚Р°
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status_text = (
                    f"рџџў **РЎС‚Р°С‚СѓСЃ СЃРёСЃС‚РµРјС‹:** {data['status']}\n"
                    f"рџџў **LM Studio:** {'Р Р°Р±РѕС‚Р°РµС‚' if data['lm_studio'] else 'РќРµ СЂР°Р±РѕС‚Р°РµС‚'}\n"
                    f"рџџў **Cursor:** {'Р”РѕСЃС‚СѓРїРµРЅ' if data['cursor_available'] else 'РќРµ РґРѕСЃС‚СѓРїРµРЅ'}\n"
                    f"рџџў **API Agent:** Р Р°Р±РѕС‚Р°РµС‚ РЅР° РїРѕСЂС‚Сѓ 8088"
                )
            else:
                status_text = "рџ”ґ **API Agent РЅРµ РѕС‚РІРµС‡Р°РµС‚**"
                
        except Exception as e:
            status_text = f"рџ”ґ **РћС€РёР±РєР° РїСЂРѕРІРµСЂРєРё СЃС‚Р°С‚СѓСЃР°:** {str(e)}"
            
        await update.message.reply_text(status_text)
    
    async def create_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РЎРѕР·РґР°РЅРёРµ Р·Р°РґР°С‡Рё"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("вќЊ Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ")
            return
            
        # РџРѕР»СѓС‡Р°РµРј РѕРїРёСЃР°РЅРёРµ Р·Р°РґР°С‡Рё
        if context.args:
            task_description = " ".join(context.args)
        else:
            await update.message.reply_text("вќЊ РЈРєР°Р¶РёС‚Рµ РѕРїРёСЃР°РЅРёРµ Р·Р°РґР°С‡Рё: `/task <РѕРїРёСЃР°РЅРёРµ>`")
            return
            
        try:
            # РћС‚РїСЂР°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ РІ API Р°РіРµРЅС‚
            task_data = {
                "task": task_description,
                "project_path": "D:\\AI-Agent\\Memory",
                "timeout": 300
            }
            
            response = requests.post(f"{self.api_url}/task", json=task_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id", "unknown")
                
                await update.message.reply_text(
                    f"вњ… **Р—Р°РґР°С‡Р° СЃРѕР·РґР°РЅР°!**\n\n"
                    f"рџ“ќ **РћРїРёСЃР°РЅРёРµ:** {task_description}\n"
                    f"рџ†” **ID Р·Р°РґР°С‡Рё:** {task_id}\n"
                    f"вЏ±пёЏ **РўР°Р№РјР°СѓС‚:** 5 РјРёРЅСѓС‚\n\n"
                    f"рџ¤– AI Agent РЅР°С‡РёРЅР°РµС‚ РІС‹РїРѕР»РЅРµРЅРёРµ РІ Cursor..."
                )
                
                # Р—РґРµСЃСЊ РјРѕР¶РЅРѕ РґРѕР±Р°РІРёС‚СЊ Р»РѕРіРёРєСѓ РґР»СЏ РѕС‚СЃР»РµР¶РёРІР°РЅРёСЏ РІС‹РїРѕР»РЅРµРЅРёСЏ Р·Р°РґР°С‡Рё
                
            else:
                await update.message.reply_text(f"вќЊ **РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ Р·Р°РґР°С‡Рё:** {response.status_code}")
                
        except Exception as e:
            await update.message.reply_text(f"вќЊ **РћС€РёР±РєР°:** {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РћР±СЂР°Р±РѕС‚РєР° С‚РµРєСЃС‚РѕРІС‹С… СЃРѕРѕР±С‰РµРЅРёР№"""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("вќЊ Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰РµРЅ")
            return
            
        message_text = update.message.text
        
        # Р•СЃР»Рё СЃРѕРѕР±С‰РµРЅРёРµ РЅРµ РєРѕРјР°РЅРґР°, СЃРѕР·РґР°РµРј Р·Р°РґР°С‡Сѓ
        if not message_text.startswith('/'):
            try:
                # РћС‚РїСЂР°РІР»СЏРµРј Р·Р°РґР°С‡Сѓ РІ API Р°РіРµРЅС‚
                task_data = {
                    "task": message_text,
                    "project_path": "D:\\AI-Agent\\Memory",
                    "timeout": 300
                }
                
                response = requests.post(f"{self.api_url}/task", json=task_data, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get("task_id", "unknown")
                    
                    await update.message.reply_text(
                        f"вњ… **Р—Р°РґР°С‡Р° РїСЂРёРЅСЏС‚Р°!**\n\n"
                        f"рџ“ќ **РћРїРёСЃР°РЅРёРµ:** {message_text}\n"
                        f"рџ†” **ID Р·Р°РґР°С‡Рё:** {task_id}\n"
                        f"вЏ±пёЏ **РўР°Р№РјР°СѓС‚:** 5 РјРёРЅСѓС‚\n\n"
                        f"рџ¤– AI Agent РІС‹РїРѕР»РЅСЏРµС‚ Р·Р°РґР°С‡Сѓ РІ Cursor..."
                    )
                    
                else:
                    await update.message.reply_text(f"вќЊ **РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ Р·Р°РґР°С‡Рё:** {response.status_code}")
                    
            except Exception as e:
                await update.message.reply_text(f"вќЊ **РћС€РёР±РєР°:** {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """РћР±СЂР°Р±РѕС‚С‡РёРє РѕС€РёР±РѕРє"""
        logger.error(f"Update {update} caused error {context.error}")

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("вќЊ РћС€РёР±РєР°: РќРµ СѓРєР°Р·Р°РЅ TELEGRAM_BOT_TOKEN")
        print("РЎРѕР·РґР°Р№С‚Рµ Р±РѕС‚Р° С‡РµСЂРµР· @BotFather Рё СѓСЃС‚Р°РЅРѕРІРёС‚Рµ С‚РѕРєРµРЅ:")
        print("set TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    # РЎРѕР·РґР°РµРј Р±РѕС‚Р°
    bot = AIAgentBot()
    
    # РЎРѕР·РґР°РµРј РїСЂРёР»РѕР¶РµРЅРёРµ
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Р”РѕР±Р°РІР»СЏРµРј РѕР±СЂР°Р±РѕС‚С‡РёРєРё
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("task", bot.create_task))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_error_handler(bot.error_handler)
    
    # Р—Р°РїСѓСЃРєР°РµРј Р±РѕС‚Р°
    print("рџ¤– Р—Р°РїСѓСЃРє Telegram Р±РѕС‚Р°...")
    print(f"рџ”‘ РўРѕРєРµРЅ: {BOT_TOKEN[:10]}...")
    print(f"рџ‘Ґ Р Р°Р·СЂРµС€РµРЅРЅС‹Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»Рё: {ALLOWED_USERS}")
    print("рџ“± Р‘РѕС‚ РіРѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ!")
    
    application.run_polling()

if __name__ == "__main__":
    main()


