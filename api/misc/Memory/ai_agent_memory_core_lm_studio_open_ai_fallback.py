#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Agent Memory Core for Windows (LM Studio + OpenAI fallback)
-------------------------------------------------------------
Features:
- Persistent chat memory in SQLite (sessions + messages)
- Works with LM Studio (OpenAI-compatible /v1/chat/completions)
- Automatic fallback to OpenAI if LM Studio is unavailable or errors
- Simple CLI for quick tests; can be imported as a module
- Russian system prompt; concise + witty when appropriate

Usage (Windows PowerShell):
  python agent_with_memory.py --session "default"

Env vars (optional):
  OPENAI_API_KEY: for fallback
  LM_STUDIO_URL:  default http://127.0.0.1:1234
  LM_STUDIO_MODEL: default deepseek-r1-distill-qwen-14b-abliterated-v2
  OPENAI_MODEL:    default gpt-4o-mini

DB file: ./agent_memory.sqlite
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from typing import List, Dict

import requests

# ---------------------- Configuration ----------------------
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234")
LM_STUDIO_MODEL = os.getenv(
    "LM_STUDIO_MODEL",
    "deepseek-r1-distill-qwen-14b-abliterated-v2",
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DB_PATH = os.getenv("AGENT_DB", os.path.join(os.path.dirname(__file__), "agent_memory.sqlite"))
SYSTEM_PROMPT = (
    "РўС‹ вЂ” РїРѕРјРѕС‰РЅРёРє Р’Р°С‚СЃРѕРЅ. РћС‚РІРµС‡Р°Р№ РєСЂР°С‚РєРѕ, РЅР° СЂСѓСЃСЃРєРѕРј. \n"
    "Р‘СѓРґСЊ РґСЂСѓР¶РµР»СЋР±РЅС‹Рј Рё РѕСЃС‚СЂРѕСѓРјРЅС‹Рј, РєРѕРіРґР° СѓРјРµСЃС‚РЅРѕ. \n"
    "Р•СЃР»Рё РёРЅС„РѕСЂРјР°С†РёРё РЅРµ С…РІР°С‚Р°РµС‚ вЂ” СЃРєР°Р¶Рё РѕР± СЌС‚РѕРј Рё РїСЂРµРґР»РѕР¶Рё С€Р°РіРё."
)

# ---------------------- Database layer ----------------------
DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('system','user','assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_messages_session_time ON messages(session_id, created_at);
"""


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db_connect() as c:
        for stmt in filter(None, DDL.split(";")):
            s = stmt.strip()
            if s:
                c.execute(s)
        c.commit()


def get_or_create_session(name: str) -> int:
    with db_connect() as c:
        cur = c.execute("SELECT id FROM sessions WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        now = datetime.utcnow().isoformat()
        c.execute("INSERT INTO sessions(name, created_at) VALUES (?, ?)", (name, now))
        c.commit()
        return c.execute("SELECT id FROM sessions WHERE name = ?", (name,)).fetchone()["id"]


def add_message(session_id: int, role: str, content: str) -> None:
    with db_connect() as c:
        c.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.utcnow().isoformat()),
        )
        c.commit()


def fetch_context(session_id: int, limit: int = 24) -> List[Dict[str, str]]:
    """Return system + last N messages as OpenAI-style list."""
    with db_connect() as c:
        cur = c.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit),
        )
        rows = list(cur.fetchall())[::-1]  # chronological
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs.extend({"role": r["role"], "content": r["content"]} for r in rows)
    return msgs

# ---------------------- Model clients ----------------------
class ModelError(Exception):
    pass


def chat_lm_studio(messages: List[Dict[str, str]], timeout: int = 45) -> str:
    url = f"{LM_STUDIO_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800,
    }
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code != 200:
            raise ModelError(f"LM Studio HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        raise ModelError(f"LM Studio error: {e}")


def chat_openai(messages: List[Dict[str, str]], timeout: int = 45) -> str:
    if not OPENAI_API_KEY:
        raise ModelError("No OPENAI_API_KEY provided")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if r.status_code != 200:
            raise ModelError(f"OpenAI HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        raise ModelError(f"OpenAI error: {e}")


# ---------------------- Orchestrator ----------------------

def respond(session_id: int, user_text: str, k_ctx: int = 24) -> str:
    add_message(session_id, "user", user_text)
    messages = fetch_context(session_id, limit=k_ctx)

    # Try LM Studio first
    try:
        reply = chat_lm_studio(messages)
        add_message(session_id, "assistant", reply)
        return reply
    except ModelError as e1:
        # Fallback to OpenAI
        try:
            reply = chat_openai(messages)
            add_message(session_id, "assistant", reply)
            return reply + "\n\n(РћС‚РІРµС‚ РїРѕР»СѓС‡РµРЅ С‡РµСЂРµР· fallback OpenAI)"
        except ModelError as e2:
            err = (
                "вљ пёЏ РћР±Р° РґРІРёР¶РєР° РЅРµРґРѕСЃС‚СѓРїРЅС‹.\n"
                f"LM Studio: {e1}\nOpenAI: {e2}\n"
                "РџСЂРѕРІРµСЂСЊ LM Studio (Р·Р°РїСѓС‰РµРЅ Р»Рё СЃРµСЂРІРµСЂ РЅР° 127.0.0.1:1234) Рё/РёР»Рё РєР»СЋС‡ OPENAI_API_KEY."
            )
            add_message(session_id, "assistant", err)
            return err


# ---------------------- CLI ----------------------

def main():
    parser = argparse.ArgumentParser(description="AI-Agent with SQLite memory and fallback")
    parser.add_argument("--session", default="default", help="РРјСЏ СЃРµСЃСЃРёРё (РєР°РЅР°Р»Р°)")
    parser.add_argument("--once", help="РћРґРЅРѕСЂР°Р·РѕРІС‹Р№ Р·Р°РїСЂРѕСЃ (Р±РµР· РёРЅС‚РµСЂР°РєС‚РёРІР°)")
    args = parser.parse_args()

    init_db()
    sid = get_or_create_session(args.session)

    if args.once:
        print(respond(sid, args.once))
        return

    print(f"РЎРµСЃСЃРёСЏ: {args.session}. Р’РІРµРґРёС‚Рµ С‚РµРєСЃС‚ (Ctrl+C РґР»СЏ РІС‹С…РѕРґР°).\n")
    try:
        while True:
            user_text = input("Р’С‹: ").strip()
            if not user_text:
                continue
            reply = respond(sid, user_text)
            print("Р’Р°С‚СЃРѕРЅ:", reply, "\n")
    except (KeyboardInterrupt, EOFError):
        print("\nР”Рѕ СЃРІСЏР·Рё! рџ––")


if __name__ == "__main__":
    main()
