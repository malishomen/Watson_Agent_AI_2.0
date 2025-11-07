#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Operator - РРЎРџР РђР’Р›Р•РќРќРђРЇ Р’Р•Р РЎРРЇ
РРЎРџР РђР’Р›Р•РќРђ РџР РћР‘Р›Р•РњРђ РЎ РљРћР”РР РћР’РљРћР™ LATIN-1
"""
import os, logging, asyncio
import aiohttp
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# РџСЂРёРЅСѓРґРёС‚РµР»СЊРЅРѕ СѓСЃС‚Р°РЅР°РІР»РёРІР°РµРј UTF-8 РєРѕРґРёСЂРѕРІРєСѓ
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

API_URL = os.getenv("AGENT_HTTP_URL", "http://127.0.0.1:8088")
SECRET = os.getenv("AGENT_HTTP_SHARED_SECRET", "change_me")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED = [x.strip() for x in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",") if x.strip()]
ADMIN = os.getenv("TELEGRAM_ADMIN_USER_ID", "")

SESSION_DEFAULT = "Danil-PC"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tg")

def is_allowed(user_id: int) -> bool:
    return (not ALLOWED) or (str(user_id) in ALLOWED)

async def api_get(session: aiohttp.ClientSession, path: str):
    """GET Р·Р°РїСЂРѕСЃ СЃ РїСЂР°РІРёР»СЊРЅРѕР№ РєРѕРґРёСЂРѕРІРєРѕР№"""
    headers = {
        "x-agent-secret": SECRET,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Accept-Charset": "utf-8"
    }
    async with session.get(f"{API_URL}{path}", headers=headers) as r:
        return await r.json()

async def api_post(session: aiohttp.ClientSession, path: str, payload: dict):
    """POST Р·Р°РїСЂРѕСЃ СЃ РїСЂР°РІРёР»СЊРЅРѕР№ РєРѕРґРёСЂРѕРІРєРѕР№"""
    headers = {
        "x-agent-secret": SECRET,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Accept-Charset": "utf-8"
    }
    async with session.post(f"{API_URL}{path}", headers=headers, json=payload) as r:
        return await r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    await update.message.reply_text("Р“РѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ. /ping, /pwd, /cd <path>, /cmd <С‚РµРєСЃС‚>, /approve <ID>, /run_spec <path>")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    async with aiohttp.ClientSession() as s:
        data = await api_get(s, "/health")
    await update.message.reply_text(f"API: {data}")

async def pwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    async with aiohttp.ClientSession() as s:
        data = await api_get(s, "/workdir")
    await update.message.reply_text(f"{data.get('stdout','')}")

async def cd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    if not context.args:
        await update.message.reply_text("РЎРёРЅС‚Р°РєСЃРёСЃ: /cd D:\\РїСѓС‚СЊ")
        return
    path = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/cd", {"session": SESSION_DEFAULT, "path": path})
    await update.message.reply_text(data.get("stdout","") or data.get("stderr",""))

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    if not context.args:
        await update.message.reply_text("РЎРёРЅС‚Р°РєСЃРёСЃ: /cmd <РєРѕРјР°РЅРґР° Р»РёР±Рѕ РѕР±С‹С‡РЅС‹Р№ Р·Р°РїСЂРѕСЃ>")
        return
    command = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/command", {"session": SESSION_DEFAULT, "command": command})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(РїСѓСЃС‚Рѕ)")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if str(uid) != str(ADMIN):
        await update.message.reply_text("РўРѕР»СЊРєРѕ Р°РґРјРёРЅ РјРѕР¶РµС‚ РїРѕРґС‚РІРµСЂР¶РґР°С‚СЊ.")
        return
    if not context.args:
        await update.message.reply_text("РЎРёРЅС‚Р°РєСЃРёСЃ: /approve AP-123456789")
        return
    approval_id = context.args[0]
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/approve", {"session": SESSION_DEFAULT, "approval_id": approval_id})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(РїСѓСЃС‚Рѕ)")

async def run_spec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Р”РѕСЃС‚СѓРї Р·Р°РїСЂРµС‰С‘РЅ.")
        return
    if not context.args:
        await update.message.reply_text("РЎРёРЅС‚Р°РєСЃРёСЃ: /run_spec D:\\AI-Agent\\ProjectSpec.yml")
        return
    spec = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/run-spec", {"spec_path": spec})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(РїСѓСЃС‚Рѕ)")

async def main():
    if not BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN РЅРµ Р·Р°РґР°РЅ")
    
    # РќР°СЃС‚СЂР°РёРІР°РµРј Application СЃ РїСЂР°РІРёР»СЊРЅРѕР№ РєРѕРґРёСЂРѕРІРєРѕР№
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Р”РѕР±Р°РІР»СЏРµРј РѕР±СЂР°Р±РѕС‚С‡РёРєРё РєРѕРјР°РЅРґ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("pwd", pwd))
    app.add_handler(CommandHandler("cd", cd))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("run_spec", run_spec))
    
    logging.info("Telegram operator started (РРЎРџР РђР’Р›Р•РќРќРђРЇ Р’Р•Р РЎРРЇ)")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    import asyncio
    import sys
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

