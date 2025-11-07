#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watson Agent 2.0 - Telegram Bridge
Long-polling мост между Telegram ботом и локальным API автокодера.
"""
import os
import json
import time
import sys
import re
import subprocess
import requests
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# Добавляем путь к utils для импорта роутера
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # опционально: если фикс. чат
API_BASE = os.getenv("WATSON_API_BASE", "http://127.0.0.1:8090")
REPO_PATH = os.getcwd()  # корень workspace Cursor
PROJECTS_ROOT = r"D:\projects\Projects_by_Watson_Local_Agent"
POLL_INTERVAL = 1.5
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "session_state.json")
LOCK_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "telegram_bridge.lock")

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Regex для парсинга OPS команд
HOST_RE = re.compile(r"(?:host\s*=\s*|^host\s+)(?P<host>[a-zA-Z0-9\.\-:_]+)", re.IGNORECASE)
REF_RE  = re.compile(r"(?:ref\s*=\s*|^ref\s+)(?P<ref>[A-Za-z0-9_\-\.\/]+)", re.IGNORECASE)
TAG_RE  = re.compile(r"(?:tag\s*=\s*|^tag\s+)(?P<tag>[A-Za-z0-9_\-\.]+)", re.IGNORECASE)
TO_RE   = re.compile(r"(?:to\s*=\s*|^to\s+)(?P<to>[A-Za-z0-9_\-\.]+)", re.IGNORECASE)


# ============ PID Lock для одиночного экземпляра ============
def acquire_lock():
    """Проверяет и создаёт lock-файл. Выходит если уже запущен."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # Проверяем жив ли процесс
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                PROCESS_QUERY_INFORMATION = 0x0400
                handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, old_pid)
                if handle:
                    kernel32.CloseHandle(handle)
                    print(f"❌ Telegram Bridge уже запущен (PID: {old_pid})")
                    sys.exit(1)
            else:
                # Unix-like
                try:
                    os.kill(old_pid, 0)
                    print(f"❌ Telegram Bridge уже запущен (PID: {old_pid})")
                    sys.exit(1)
                except OSError:
                    pass
            # Процесс мёртв - удаляем старый lock
            os.remove(LOCK_FILE)
        except:
            pass
    
    # Создаём lock с текущим PID
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    print(f"🔒 Lock acquired (PID: {os.getpid()})")


def release_lock():
    """Удаляет lock-файл при выходе."""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            print("🔓 Lock released")
    except:
        pass


# ============ Session State Management ============
def _load_state():
    """Загружает состояние сессий из JSON файла."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading state: {e}", file=sys.stderr)
    return {}


def _save_state(state):
    """Сохраняет состояние сессий в JSON файл."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving state: {e}", file=sys.stderr)


STATE = _load_state()


def set_chat_project(chat_id, path):
    """Устанавливает текущий проект для чата."""
    STATE[str(chat_id)] = {"repo_path": path}
    _save_state(STATE)


def get_chat_project(chat_id):
    """Возвращает текущий проект для чата или None."""
    return (STATE.get(str(chat_id)) or {}).get("repo_path")


def http_get(url, params=None, timeout=30):
    if params:
        url = f"{url}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        raise  # Re-raise для обработки выше


def http_post(url, data, timeout=60):
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def tg_send(chat_id, text):
    try:
        http_get(f"{TG_API}/sendMessage", {"chat_id": chat_id, "text": text[:4000]})
    except Exception as e:
        print(f"TG send error: {e}", file=sys.stderr)


def format_tail(s, limit=1200):
    if not s:
        return ""
    return s if len(s) <= limit else ("…" + s[-limit:])


def slugify(name: str) -> str:
    """Преобразует название проекта в безопасное имя директории."""
    # Транслитерация кириллицы (упрощённая)
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    result = []
    for char in name.lower():
        if char in translit:
            result.append(translit[char])
        elif char.isalnum() or char == '_':
            result.append(char)
        elif char in ' -':
            result.append('_')
    
    slug = ''.join(result)
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug[:50] if slug else 'new_project'


def do_project_create(chat_id, project_name):
    """Создаёт новый проект через PROJECT_TEMPLATE.ps1 и автоматически переключает контекст."""
    safe_name = slugify(project_name)
    target_dir = os.path.join(PROJECTS_ROOT, safe_name)
    
    tg_send(chat_id, f"📁 Создаю проект: {safe_name}\nПуть: {PROJECTS_ROOT}")
    
    try:
        os.makedirs(PROJECTS_ROOT, exist_ok=True)
        
        # Вызываем PowerShell скрипт
        ps_script = os.path.join(REPO_PATH, "scripts", "PROJECT_TEMPLATE.ps1")
        cmd = [
            "pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", ps_script,
            "-Name", safe_name,
            "-Path", PROJECTS_ROOT
        ]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        
        if proc.returncode == 0 and os.path.exists(target_dir):
            # Автоматически переключаем контекст на новый проект
            set_chat_project(chat_id, target_dir)
            
            tg_send(chat_id, 
                   f"✅ Проект создан и активирован!\n\n"
                   f"📂 Путь: {target_dir}\n"
                   f"📝 Структура:\n"
                   f"  - src/main.py\n"
                   f"  - tests/test_main.py\n"
                   f"  - README.md\n"
                   f"  - .gitignore\n"
                   f"  - requirements.txt\n\n"
                   f"💡 Команды:\n"
                   f"  /where - показать текущий проект\n"
                   f"  /list - список всех проектов\n"
                   f"  /use {safe_name} - переключить проект\n\n"
                   f"🎯 Теперь все /run будут в этом проекте:\n"
                   f"  /run Add detailed README\n"
                   f"  /run Add type hints to src/main.py")
        else:
            error_msg = proc.stderr or proc.stdout or "Unknown error"
            tg_send(chat_id, f"💥 Ошибка создания проекта:\n{error_msg[:500]}")
            
    except subprocess.TimeoutExpired:
        tg_send(chat_id, "💥 Timeout при создании проекта (> 60 сек)")
    except Exception as e:
        tg_send(chat_id, f"💥 Ошибка: {str(e)[:500]}")


def run_task_from_text(chat_id, text):
    """
    Использует новый endpoint /relay/submit для универсальной обработки задач.
    Команды:
    /ping - проверка связи
    /help - справка
    /dryrun <задача> → dry_run = true
    /run <задача>    → dry_run = false
    /smoke host=<host> - staging smoke check
    /deploy host=<host> ref=<main|branch> - deploy to staging
    /promote host=<host> tag=<image_tag> - promote image to staging
    /rollback host=<host> to=<prev|tag> - rollback version
    Любой текст → /relay/submit → роутинг
    """
    text_lower = text.strip().lower()
    
    # Служебные команды (локальные)
    if text_lower == "/ping":
        tg_send(chat_id, "🏓 pong! Watson Agent 2.0 готов к работе.")
        return
    
    if text_lower == "/where":
        current = get_chat_project(chat_id)
        if current:
            tg_send(chat_id, f"📂 Текущий проект:\n{current}")
        else:
            tg_send(chat_id, f"📂 Проект не выбран.\n\nИспользуйте:\n  /list - показать проекты\n  /use <имя> - выбрать проект")
        return
    
    if text_lower == "/list":
        try:
            if not os.path.exists(PROJECTS_ROOT):
                tg_send(chat_id, f"📁 Папка проектов не найдена:\n{PROJECTS_ROOT}")
                return
            projects = [d for d in os.listdir(PROJECTS_ROOT) 
                       if os.path.isdir(os.path.join(PROJECTS_ROOT, d)) and not d.startswith('.')]
            if projects:
                current = get_chat_project(chat_id)
                items = []
                for p in sorted(projects[:50]):
                    marker = "📌" if current and current.endswith(p) else "📁"
                    items.append(f"{marker} {p}")
                tg_send(chat_id, f"📁 Проекты ({len(projects)}):\n\n" + "\n".join(items))
            else:
                tg_send(chat_id, f"📁 Нет проектов в:\n{PROJECTS_ROOT}\n\nСоздайте: создай проект <название>")
        except Exception as e:
            tg_send(chat_id, f"💥 Ошибка чтения проектов: {str(e)[:300]}")
        return
    
    if text_lower.startswith("/use "):
        proj_name = text[5:].strip()
        safe_name = slugify(proj_name)
        target = os.path.join(PROJECTS_ROOT, safe_name)
        if os.path.isdir(target):
            set_chat_project(chat_id, target)
            tg_send(chat_id, f"✅ Проект активирован:\n{target}\n\nВсе /run теперь будут в этом проекте.")
        else:
            tg_send(chat_id, f"⚠️ Проект не найден: {safe_name}\n\nИспользуйте /list для просмотра.")
        return
    
    # ========== OPS: /smoke ==========
    if text.lower().startswith("/smoke"):
        m = HOST_RE.search(text)
        host = m.group("host") if m else None
        if not host:
            tg_send(chat_id, "Укажи хост: /smoke host=<staging-host>")
            return
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/smoke", json={"host": host, "timeout": 60}, timeout=70)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    msg_ok = (
                        "✅ Staging-smoke OK\n"
                        f"host: {host}\n"
                        f"image_tag: {data.get('image_tag')}\n"
                        f"git_sha: {data.get('git_sha')}\n"
                        f"duration: {data.get('duration_sec')}s"
                    )
                    tg_send(chat_id, msg_ok)
                else:
                    tg_send(chat_id, f"🔴 Smoke FAILED: {data}")
            else:
                tg_send(chat_id, f"🔴 Smoke HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Smoke error: {e}")
        return

    # ========== OPS: /deploy ==========
    if text.lower().startswith("/deploy"):
        mH = HOST_RE.search(text); mR = REF_RE.search(text)
        host = mH.group("host") if mH else None
        ref  = mR.group("ref")  if mR else "main"
        if not host:
            tg_send(chat_id, "Укажи хост: /deploy host=<staging-host> ref=<main|branch>")
            return
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/deploy", json={"host": host, "ref": ref, "timeout": 180}, timeout=200)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Deploy OK\nhost: {host}\nref: {ref}\n{(d.get('output') or '')[:400]}")
            else:
                tg_send(chat_id, f"🔴 Deploy FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Deploy error: {e}")
        return

    # ========== OPS: /promote ==========
    if text.lower().startswith("/promote"):
        mH = HOST_RE.search(text); mT = TAG_RE.search(text)
        host = mH.group("host") if mH else None
        tag  = mT.group("tag")  if mT else None
        if not (host and tag):
            tg_send(chat_id, "Формат: /promote host=<staging-host> tag=<image_tag>")
            return
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/promote", json={"host": host, "tag": tag, "timeout": 120}, timeout=150)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Promote OK\nhost: {host}\ntag: {tag}\n{(d.get('output') or '')[:400]}")
            else:
                tg_send(chat_id, f"🔴 Promote FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Promote error: {e}")
        return

    # ========== OPS: /rollback ==========
    if text.lower().startswith("/rollback"):
        mH = HOST_RE.search(text); mTo = TO_RE.search(text)
        host = mH.group("host") if mH else None
        to   = mTo.group("to")  if mTo else "prev"
        if not host:
            tg_send(chat_id, "Формат: /rollback host=<staging-host> to=<prev|tag>")
            return
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/rollback", json={"host": host, "to": to, "timeout": 120}, timeout=150)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Rollback OK\nhost: {host}\nto: {to}\n{(d.get('output') or '')[:400]}")
            else:
                tg_send(chat_id, f"🔴 Rollback FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Rollback error: {e}")
        return

    if text_lower.strip() == "/run":
        tg_send(chat_id, "ℹ️ Использование: /run <задача>\n\nПример:\n  /run Add detailed README")
        return
    
    if text_lower.strip() == "/dryrun":
        tg_send(chat_id, "ℹ️ Использование: /dryrun <задача>\n\nПример:\n  /dryrun Add type hints to main.py")
        return
    
    if text_lower in ("/help", "/start"):
        tg_send(chat_id, 
                "🤖 Watson Agent 2.0 (Conveyor v1)\n\n"
                "📝 Команды:\n"
                "/ping - проверка связи\n"
                "/where - текущий проект\n"
                "/list - список проектов\n"
                "/use <имя> - выбрать проект\n"
                "/run <задача> - применить патч\n"
                "/dryrun <задача> - показать diff\n\n"
                "🚀 OPS команды:\n"
                "/smoke host=<host> - staging smoke check\n"
                "/deploy host=<host> ref=<main|branch> - deploy to staging\n"
                "/promote host=<host> tag=<image_tag> - promote image\n"
                "/rollback host=<host> to=<prev|tag> - rollback version\n\n"
                "🆕 Создание:\n"
                "создай проект <название>\n\n"
                "💡 Можно писать простыми словами:\n"
                "• сделай логирование в safe_call\n"
                "• добавь типы в api/agent.py\n\n"
                "DeepSeek-R1 → Qwen2.5-Coder → код")
        return
    
    # Определяем явные команды
    dry_run = False
    task_text = text.strip()
    
    if task_text.lower().startswith("/dryrun"):
        dry_run = True
        task_text = task_text[7:].strip()
    elif task_text.lower().startswith("/run"):
        dry_run = False
        task_text = task_text[4:].strip()
    elif task_text.startswith("/"):
        # Неизвестная команда
        tg_send(chat_id, "ℹ️ Неизвестная команда. Используйте /help для справки.")
        return

    if not task_text.strip():
        tg_send(chat_id, "⚠️ Пустая задача. Используйте /help для примеров.")
        return
    
    # ===== Натуральные фразы OPS =====
    low = text.lower()
    if "smoke" in low and "staging" in low:
        m = HOST_RE.search(text)
        if not m:
            tg_send(chat_id, "Формат: /smoke host=<staging-host>")
            return
        host = m.group("host")
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/smoke", json={"host": host, "timeout": 60}, timeout=70)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Staging-smoke OK\nhost: {host}\nimage_tag: {d.get('image_tag')}\ngit_sha: {d.get('git_sha')}\nduration: {d.get('duration_sec')}s")
            else:
                tg_send(chat_id, f"🔴 Smoke FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Smoke error: {e}")
        return

    if "deploy" in low and "staging" in low:
        mH = HOST_RE.search(text); mR = REF_RE.search(text)
        if not mH:
            tg_send(chat_id, "Формат: /deploy host=<staging-host> ref=<main|branch>")
            return
        host = mH.group("host"); ref = mR.group("ref") if mR else "main"
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/deploy", json={"host": host, "ref": ref, "timeout": 180}, timeout=200)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Deploy OK\nhost: {host}\nref: {ref}\n{(d.get('output') or '')[:350]}")
            else:
                tg_send(chat_id, f"🔴 Deploy FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Deploy error: {e}")
        return

    if "promote" in low and "staging" in low:
        mH = HOST_RE.search(text); mT = TAG_RE.search(text)
        if not (mH and mT):
            tg_send(chat_id, "Формат: /promote host=<staging-host> tag=<image_tag>")
            return
        host = mH.group("host"); tag = mT.group("tag")
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/promote", json={"host": host, "tag": tag, "timeout": 120}, timeout=150)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Promote OK\nhost: {host}\ntag: {tag}\n{(d.get('output') or '')[:350]}")
            else:
                tg_send(chat_id, f"🔴 Promote FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Promote error: {e}")
        return

    if "rollback" in low:
        mH = HOST_RE.search(text); mTo = TO_RE.search(text)
        if not mH:
            tg_send(chat_id, "Формат: /rollback host=<staging-host> to=<prev|tag>")
            return
        host = mH.group("host"); to = mTo.group("to") if mTo else "prev"
        try:
            api = os.environ.get("WATSON_API_BASE") or "http://127.0.0.1:8090"
            r = requests.post(f"{api}/ops/rollback", json={"host": host, "to": to, "timeout": 120}, timeout=150)
            if r.status_code == 200 and r.json().get("ok"):
                d = r.json()
                tg_send(chat_id, f"✅ Rollback OK\nhost: {host}\nto: {to}\n{(d.get('output') or '')[:350]}")
            else:
                tg_send(chat_id, f"🔴 Rollback FAIL: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            tg_send(chat_id, f"🔴 Rollback error: {e}")
        return

    # Получаем текущий проект для чата
    target_repo = get_chat_project(chat_id) or REPO_PATH
    repo_name = os.path.basename(target_repo)
    
    tg_send(chat_id, f"🤖 Обрабатываю задачу...\n📂 Repo: {repo_name}")

    # Отправляем в /relay/submit
    body = {
        "text": task_text,
        "dry_run": dry_run,
        "chat_id": str(chat_id)
    }

    try:
        res = http_post(f"{API_BASE}/relay/submit", body, timeout=300)
        error_counter["consecutive_fails"] = 0  # Сброс при успехе
    except Exception as e:
        err_msg = str(e)
        error_counter["consecutive_fails"] += 1
        
        # Алерт при 3 подряд FAIL
        if error_counter["consecutive_fails"] >= 3:
            send_alert(f"3 consecutive API failures!\nLast error: {err_msg[:200]}")
            error_counter["consecutive_fails"] = 0  # Сброс после алерта
        
        # Проверка порта занят
        if "Connection refused" in err_msg or "port" in err_msg.lower():
            error_counter["port_errors"] += 1
            if error_counter["port_errors"] >= 2:
                send_alert(f"API port issue detected!\n{err_msg[:200]}")
                error_counter["port_errors"] = 0
        
        if "DeepSeek" in err_msg or "LLM" in err_msg:
            tg_send(chat_id, f"⚠️ DeepSeek временно недоступен. Попробую выполнить напрямую...\n{err_msg[:200]}")
        else:
            tg_send(chat_id, f"💥 Ошибка вызова API: {err_msg[:300]}")
        return

    ok = res.get("ok")
    intent = res.get("intent")
    response = res.get("response")
    error = res.get("error")
    
    if not ok:
        tg_send(chat_id, f"❌ Ошибка: {error or 'Unknown error'}")
        return
    
    # Обработка по intent
    if intent in ("help", "ping", "noncode"):
        tg_send(chat_id, response or "OK")
        return
    
    if intent == "project_create":
        proj_name = res.get("project_name")
        proj_path = res.get("project_path")
        if proj_name and proj_path:
            # Автоматически переключаем контекст
            set_chat_project(chat_id, proj_path)
            tg_send(chat_id, 
                   f"✅ Проект создан и активирован!\n\n"
                   f"📂 {proj_path}\n\n"
                   f"💡 Команды:\n"
                   f"/where - текущий проект\n"
                   f"/list - все проекты\n"
                   f"/run <задача> - выполнить в проекте")
        else:
            tg_send(chat_id, response or "Проект создан")
        return
    
    if intent == "code":
        diff = res.get("diff")
        logs = res.get("logs", "")
        
        status_parts = []
        if dry_run:
            status_parts.append("🧪 DRY-RUN")
        else:
            status_parts.append("✅ APPLIED")
        
        if diff:
            status_parts.append(f"Diff: {len(diff)} bytes")
        
        msg = f"{' | '.join(status_parts)}\n📂 Repo: {repo_name}\n\n"
        if response:
            msg += f"{response}\n\n"
        if logs:
            msg += f"Logs:\n{format_tail(logs, 800)}"
        
        tg_send(chat_id, msg)
        return
    
    # Fallback
    tg_send(chat_id, response or f"Intent: {intent}")


def send_alert(message: str):
    """Отправка алерта в Telegram"""
    if CHAT_ID:
        try:
            tg_send(CHAT_ID, f"⚠️ ALERT\n{message}")
        except:
            pass


# Счётчик ошибок для алертов
error_counter = {"consecutive_fails": 0, "port_errors": 0}


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Missing TELEGRAM_TOKEN in environment", file=sys.stderr)
        sys.exit(1)

    # Проверяем и захватываем lock (одиночный экземпляр)
    try:
        acquire_lock()
    except SystemExit as e:
        if e.code == 1:
            # Уже запущен - отправляем алерт
            send_alert("Telegram Bridge уже запущен (409 conflict)")
            raise
    
    try:
        print(f"🤖 Watson Telegram Bridge starting...")
        print(f"   API: {API_BASE}")
        print(f"   Repo: {REPO_PATH}")
        print(f"   Chat filter: {CHAT_ID or 'ANY'}")

        # Отправляем приветствие
        if CHAT_ID:
            tg_send(CHAT_ID, "🤖 Watson Bridge запущен (Conveyor v1).\n\n📝 Команды:\n/run <задача> - применить и тестировать\n/dryrun <задача> - только diff\n\nМожно писать простым текстом!")

        offset = None

        while True:
            try:
                updates = http_get(f"{TG_API}/getUpdates", {"timeout": 25, "offset": offset or 0})
                
                # Если есть обновления - обрабатываем
                if updates.get("result"):
                    for upd in updates["result"]:
                        offset = upd["update_id"] + 1
                        msg = upd.get("message") or upd.get("edited_message")
                        if not msg:
                            continue
                        
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        
                        if not text:
                            tg_send(chat_id, "Я понимаю только текстовые команды.")
                            continue

                        # Если задан фикс. чат — фильтруем
                        if CHAT_ID and str(chat_id) != str(CHAT_ID):
                            continue

                        # Логируем входящую команду
                        print(f"📨 [{chat_id}]: {text[:80]}")

                        # Обрабатываем команду
                        run_task_from_text(chat_id, text)
                
                # Короткая пауза между запросами
                time.sleep(0.1)

            except KeyboardInterrupt:
                print("\n🛑 Bridge stopped by user")
                break
            except Exception as e:
                # Timeout - это нормально для long-polling, не спамим в лог
                err_str = str(e).lower()
                if "timed out" not in err_str and "timeout" not in err_str:
                    print(f"⚠️ Poll error: {e}", file=sys.stderr)
                time.sleep(POLL_INTERVAL)
    
    finally:
        # Освобождаем lock при выходе
        release_lock()


if __name__ == "__main__":
    main()

