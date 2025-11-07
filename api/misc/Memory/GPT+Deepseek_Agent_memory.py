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
import csv
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
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

# ---------------------- Security Policy ----------------------
WORKDIR = Path(os.getenv("AGENT_WORKDIR", "D:\\AI-Agent")).resolve()
WHITELIST_DIRS = [
    Path("D:\\AI-Agent").resolve(),
    Path("D:\\Projects").resolve(),
    Path("D:\\Temp").resolve(),
]
# РЅРёРєР°РєРёС… System32
OPS_LOG = Path(os.getenv("AGENT_OPS_LOG", "D:\\AI-Agent\\Memory\\ops_log.csv")).resolve()
# PENDING_APPROVALS = {}  # id -> dict(action=..., params=..., created_at=...) - С‚РµРїРµСЂСЊ РІ SQLite

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
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notes_session_time ON notes(session_id, created_at);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    params TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_approvals_status_time ON approvals(status, created_at);
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

def add_note(session_id: int, content: str) -> None:
    with db_connect() as c:
        c.execute("INSERT INTO notes(session_id, content, created_at) VALUES (?, ?, ?)",
                  (session_id, content, datetime.utcnow().isoformat()))
        c.commit()

def fetch_last_note(session_id: int) -> str | None:
    with db_connect() as c:
        r = c.execute("SELECT content FROM notes WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
                      (session_id,)).fetchone()
        return r["content"] if r else None

def fetch_notes(session_id: int, limit: int = 10) -> list[str]:
    with db_connect() as c:
        rows = c.execute("SELECT content FROM notes WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                         (session_id, limit)).fetchall()
        return [x["content"] for x in rows]

# ---------------------- Utilities ----------------------
def strip_reasoning(text: str) -> str:
    if not text:
        return text
    return re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE).strip()

def is_path_allowed(p: Path) -> bool:
    try:
        rp = p.resolve()
        return any(str(rp).startswith(str(base)) for base in WHITELIST_DIRS)
    except Exception:
        return False

def log_op(op: str, ok: bool, detail: str):
    OPS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OPS_LOG.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.utcnow().isoformat(), op, "OK" if ok else "FAIL", detail])

def need_approval_for_path(p: Path) -> bool:
    return not is_path_allowed(p)

def approvals_put(aid: str, action: str, params: dict):
    with db_connect() as c:
        c.execute("""INSERT OR REPLACE INTO approvals(id, action, params, status, created_at)
                     VALUES(?,?,?,?,?)""",
                  (aid, action, json.dumps(params, ensure_ascii=False),
                   "pending", datetime.utcnow().isoformat()))
        c.commit()

def approvals_pop(aid: str):
    with db_connect() as c:
        row = c.execute("""SELECT action, params FROM approvals
                           WHERE id=? AND status='pending'""", (aid,)).fetchone()
        if not row: return None
        c.execute("""UPDATE approvals SET status='approved', resolved_at=?
                     WHERE id=?""", (datetime.utcnow().isoformat(), aid))
        c.commit()
        return {"action": row["action"], "params": json.loads(row["params"])}

def new_approval(action: str, params: dict) -> str:
    aid = f"AP-{int(time.time()*1000)}"
    approvals_put(aid, action, params)
    return aid

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
        return strip_reasoning(data["choices"][0]["message"]["content"].strip())
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
        return strip_reasoning(data["choices"][0]["message"]["content"].strip())
    except requests.RequestException as e:
        raise ModelError(f"OpenAI error: {e}")


# ---------------------- Windows Commands ----------------------
def run_exe(path: str, args: str = "", cwd: str | None = None) -> str:
    exe = Path(path)
    if need_approval_for_path(exe):
        return f"РўСЂРµР±СѓРµС‚СЃСЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ: /approve {new_approval('run_exe', {'path': path, 'args': args, 'cwd': cwd})}"
    cmd = f'"{exe}" {args}'.strip()
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or str(WORKDIR), timeout=120)
        out = (r.stdout or "") + ("\nERR:\n" + r.stderr if r.stderr else "")
        log_op("run_exe", r.returncode == 0, f"{cmd} @ {cwd or WORKDIR}")
        return out.strip() or "(РїСѓСЃС‚Рѕ)"
    except Exception as e:
        log_op("run_exe", False, f"{cmd} -> {e}")
        return f"РћС€РёР±РєР° Р·Р°РїСѓСЃРєР°: {e}"

def read_file(path: str) -> str:
    p = Path(path)
    try:
        if need_approval_for_path(p):
            return f"РўСЂРµР±СѓРµС‚СЃСЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ: /approve {new_approval('read_file', {'path': path})}"
        text = p.read_text(encoding="utf-8", errors="ignore")
        log_op("read_file", True, str(p))
        return text
    except Exception as e:
        log_op("read_file", False, f"{p} -> {e}")
        return f"РћС€РёР±РєР° С‡С‚РµРЅРёСЏ: {e}"

def write_file(path: str, text: str) -> str:
    p = Path(path)
    try:
        if need_approval_for_path(p):
            return f"РўСЂРµР±СѓРµС‚СЃСЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ: /approve {new_approval('write_file', {'path': path, 'text': text})}"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        log_op("write_file", True, str(p))
        return f"OK: Р·Р°РїРёСЃР°РЅРѕ {len(text)} СЃРёРјРІРѕР»РѕРІ РІ {p}"
    except Exception as e:
        log_op("write_file", False, f"{p} -> {e}")
        return f"РћС€РёР±РєР° Р·Р°РїРёСЃРё: {e}"

def stop_process(name_or_pid: str) -> str:
    try:
        cmd = (f"powershell -Command \"Stop-Process -Id {name_or_pid} -Force\"" if name_or_pid.isdigit()
               else f"powershell -Command \"Get-Process -Name '{name_or_pid}' -ErrorAction SilentlyContinue | Stop-Process -Force\"")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        ok = r.returncode == 0
        log_op("stop_process", ok, name_or_pid)
        return "OK" if ok else (r.stdout + "\n" + r.stderr).strip()
    except Exception as e:
        log_op("stop_process", False, name_or_pid + f" -> {e}")
        return f"РћС€РёР±РєР°: {e}"

def set_cwd(path: str) -> str:
    global WORKDIR
    p = Path(path).resolve()
    if not is_path_allowed(p):
        return f"РўСЂРµР±СѓРµС‚СЃСЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ: /approve {new_approval('set_cwd', {'path': path})}"
    WORKDIR = p
    try:
        set_setting("workdir", str(WORKDIR))
    except Exception:
        pass
    return f"OK: WORKDIR={WORKDIR}"

def get_cwd() -> str:
    return str(WORKDIR)

def get_setting(key: str, default: str | None = None) -> str | None:
    with db_connect() as c:
        row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

def set_setting(key: str, value: str) -> None:
    with db_connect() as c:
        c.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        c.commit()

# ---------------------- Orchestrator ----------------------

def respond(session_id: int, user_text: str, k_ctx: int = 24) -> str:
    add_message(session_id, "user", user_text)
    
    # Command router
    lower = user_text.strip().lower()

    if lower.startswith("/approve"):
        aid = (user_text.split(maxsplit=1)[1].strip() if len(user_text.split())>1 else "")
        item = approvals_pop(aid)
        if not item:
            reply = f"Р—Р°СЏРІРєР° {aid or '?'} РЅРµ РЅР°Р№РґРµРЅР° РёР»Рё СѓР¶Рµ РїРѕРґС‚РІРµСЂР¶РґРµРЅР°."
        else:
            act = item["action"]; params = item["params"]
            reply = (run_exe(params.get("path",""), params.get("args",""), params.get("cwd"))
                     if act=="run_exe" else
                     read_file(params.get("path","")) if act=="read_file" else
                     write_file(params.get("path",""), params.get("text","")) if act=="write_file" else
                     set_cwd(params.get("path","")) if act=="set_cwd" else
                     f"РќРµРёР·РІРµСЃС‚РЅРѕРµ РґРµР№СЃС‚РІРёРµ РІ Р·Р°СЏРІРєРµ {aid}")
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/pwd"):
        reply = get_cwd(); add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/cd"):
        path = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = set_cwd(path) if path else "РЎРёРЅС‚Р°РєСЃРёСЃ: /cd D:\\РїР°РїРєР°"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/run"):
        payload = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        if not payload:
            reply = "РЎРёРЅС‚Р°РєСЃРёСЃ: /run \"C:\\РїСѓС‚СЊ\\app.exe\" [Р°СЂРіСѓРјРµРЅС‚С‹]"
        else:
            if payload.startswith('\"'):
                try: exe, rest = payload.split('\"', 2)[1], payload.split('\"', 2)[2].strip()
                except: exe, rest = payload.strip('\"'), ""
            else:
                parts = payload.split(" ", 1); exe, rest = parts[0], (parts[1] if len(parts) > 1 else "")
            reply = run_exe(exe, rest, None)
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/read"):
        path = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = read_file(path) if path else "РЎРёРЅС‚Р°РєСЃРёСЃ: /read D:\\РїСѓС‚СЊ\\file.txt"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/write"):
        try:
            _, rest = user_text.split(" ", 1)
            fpath, text = rest.split(":::", 1)
            fpath, text = fpath.strip(), text.strip()
            if need_approval_for_path(Path(fpath)):
                reply = f"РўСЂРµР±СѓРµС‚СЃСЏ РїРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ: /approve {new_approval('write_file', {'path': fpath, 'text': text})}"
            else:
                reply = write_file(fpath, text)
        except ValueError:
            reply = "РЎРёРЅС‚Р°РєСЃРёСЃ: /write D:\\РїСѓС‚СЊ\\file.txt ::: РўР•РљРЎРў"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/kill"):
        target = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = stop_process(target) if target else "РЎРёРЅС‚Р°РєСЃРёСЃ: /kill notepad.exe РР›Р /kill 1234"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/remember"):
        content = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        if content:
            add_note(session_id, content)
            reply = f"Р—Р°РїРѕРјРЅРёР»: {content}"
        else:
            reply = "РЎРёРЅС‚Р°РєСЃРёСЃ: /remember С‚РµРєСЃС‚ Р·Р°РјРµС‚РєРё"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/recall"):
        note = fetch_last_note(session_id)
        reply = note if note else "РќРµС‚ СЃРѕС…СЂР°РЅРµРЅРЅС‹С… Р·Р°РјРµС‚РѕРє"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/notes"):
        notes = fetch_notes(session_id, 10)
        if notes:
            reply = "РџРѕСЃР»РµРґРЅРёРµ Р·Р°РјРµС‚РєРё:\n" + "\n".join(f"- {n}" for n in notes)
        else:
            reply = "РќРµС‚ СЃРѕС…СЂР°РЅРµРЅРЅС‹С… Р·Р°РјРµС‚РѕРє"
        add_message(session_id, "assistant", reply); return reply
    
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

    db_workdir = get_setting("workdir")
    if db_workdir:
        from pathlib import Path as _Path
        try:
            global WORKDIR
            WORKDIR = _Path(db_workdir).resolve()
        except Exception:
            pass

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
