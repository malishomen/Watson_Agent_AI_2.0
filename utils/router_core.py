"""
Единый роутер для Watson Agent - определяет intent и маршрутизирует задачи
"""
import re
import os
import json
import subprocess
from typing import Dict, Any, Optional

# OPS операции
_OPS_HINTS = (
    "staging-smoke",
    "smoke",
    "deploy",
    "promote",
    "rollback",
    "ansible",
    "health",
    "metrics",
)

_HOST_RE = re.compile(r"(?:host\s*=\s*|^host\s+)(?P<host>[a-zA-Z0-9\.\-:_]+)", re.IGNORECASE)
_REF_RE = re.compile(r"(?:ref\s*=\s*|^ref\s+)(?P<ref>[A-Za-z0-9_\-\.\/]+)", re.IGNORECASE)
_TAG_RE = re.compile(r"(?:tag\s*=\s*|^tag\s+)(?P<tag>[A-Za-z0-9_\-\.]+)", re.IGNORECASE)
_TO_RE  = re.compile(r"(?:to\s*=\s*|^to\s+)(?P<to>[A-Za-z0-9_\-\.]+)", re.IGNORECASE)

# Корневая директория для всех проектов
ROOT = "D:\\projects\\Projects_by_Watson_Local_Agent"

def slugify(name: str) -> str:
    """Преобразует название проекта в slug (безопасное имя директории)"""
    name = name.strip().lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name or "project"

def _parse_ops_smoke(text: str) -> Optional[Dict[str, Any]]:
    """Простейший парсер ops-задач 'staging-smoke' / '/smoke host=…'."""
    if not text:
        return None
    t = text.strip()
    if t.lower().startswith("/smoke"):
        m = _HOST_RE.search(t)
        return {"intent": "ops_smoke", "args": {"host": m.group("host") if m else None}}
    if any(k in t.lower() for k in _OPS_HINTS) and "smoke" in t.lower():
        m = _HOST_RE.search(t)
        return {"intent": "ops_smoke", "args": {"host": m.group("host") if m else None}}
    return None

def _parse_ops_deploy(text: str) -> Optional[Dict[str, Any]]:
    """'/deploy host=.. ref=..' или 'deploy to staging …' → ops_deploy."""
    if not text:
        return None
    t = text.strip().lower()
    if t.startswith("/deploy") or ("deploy" in t and ("staging" in t or "ansible" in t)):
        host = (_HOST_RE.search(text) or {}).group("host") if _HOST_RE.search(text) else None
        ref  = (_REF_RE.search(text) or {}).group("ref") if _REF_RE.search(text) else None
        return {"intent": "ops_deploy", "args": {"host": host, "ref": ref}}
    return None

def _parse_ops_promote(text: str) -> Optional[Dict[str, Any]]:
    """'/promote host=.. tag=..' или 'promote … to staging' → ops_promote."""
    if not text:
        return None
    t = text.strip().lower()
    if t.startswith("/promote") or ("promote" in t and "staging" in t):
        host = (_HOST_RE.search(text) or {}).group("host") if _HOST_RE.search(text) else None
        tag  = (_TAG_RE.search(text) or {}).group("tag") if _TAG_RE.search(text) else None
        return {"intent": "ops_promote", "args": {"host": host, "tag": tag}}
    return None

def _parse_ops_rollback(text: str) -> Optional[Dict[str, Any]]:
    """'/rollback host=.. to=..' → ops_rollback (to=prev|<tag>)."""
    if not text:
        return None
    t = text.strip().lower()
    if t.startswith("/rollback") or "rollback" in t:
        host = (_HOST_RE.search(text) or {}).group("host") if _HOST_RE.search(text) else None
        to   = (_TO_RE.search(text)  or {}).group("to")  if _TO_RE.search(text)  else None
        return {"intent": "ops_rollback", "args": {"host": host, "to": to}}
    return None

def plan_and_route(text: str, llm_client=None) -> Dict[str, Any]:
    """
    Анализирует текст задачи и определяет intent через DeepSeek
    Возвращает: {intent, normalized_text, project_name?, ...}
    """
    try:
        print(f"[ROUTER] Analyzing: {text[:100]}...")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass  # Skip emoji printing on Windows
    
    t = (text or "").strip()
    if not t:
        return {"intent": "help", "args": {}}
    
    # 1) OPS: SMOKE / DEPLOY / PROMOTE / ROLLBACK — до code
    op = _parse_ops_smoke(t)
    if op:
        return op
    op = _parse_ops_deploy(t)
    if op:
        return op
    op = _parse_ops_promote(t)
    if op:
        return op
    op = _parse_ops_rollback(t)
    if op:
        return op
    
    # Простые intent'ы без LLM
    text_lower = text.lower().strip()
    
    if text_lower in ["help", "помощь", "?", "что умеешь"]:
        return {
            "intent": "help",
            "response": """Watson Agent Conveyor v1:
- Создание проектов: 'создай проект <название>'
- Генерация кода: опиши что нужно сделать
- Ping: 'ping', 'health'
- Помощь: 'help'"""
        }
    
    if text_lower in ["ping", "health", "статус"]:
        return {
            "intent": "ping",
            "response": "🟢 Watson Agent активен"
        }
    
    # Проверка на создание проекта
    create_patterns = [
        r'создай проект (.+)',
        r'создай новый проект (.+)',
        r'new project (.+)',
        r'create project (.+)'
    ]
    
    for pattern in create_patterns:
        match = re.search(pattern, text_lower)
        if match:
            project_name = match.group(1).strip()
            return {
                "intent": "project_create",
                "project_name": project_name,
                "normalized_text": f"создать проект {project_name}"
            }
    
    # Все остальное - кодовая задача
    return {"intent": "code", "args": {"task": t}}

def do_project_create(project_name: str, repo_path: str = None) -> Dict[str, Any]:
    """Создает новый проект используя PROJECT_TEMPLATE.ps1"""
    try:
        repo_path = repo_path or ROOT
        slug = slugify(project_name)
        project_path = os.path.join(repo_path, slug)
        
        if os.path.exists(project_path):
            return {
                "ok": False,
                "error": f"Проект {slug} уже существует"
            }
        
        # Запускаем PROJECT_TEMPLATE.ps1
        template_script = os.path.join(repo_path, "scripts", "PROJECT_TEMPLATE.ps1")
        if not os.path.exists(template_script):
            return {
                "ok": False,
                "error": f"PROJECT_TEMPLATE.ps1 не найден: {template_script}"
            }
        
        cmd = ["pwsh", "-NoProfile", "-File", template_script, "-Name", project_name]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return {
                "ok": True,
                "project_name": project_name,
                "project_path": project_path,
                "output": result.stdout
            }
        else:
            return {
                "ok": False,
                "error": f"Ошибка создания проекта: {result.stderr}"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": "Таймаут создания проекта (5 минут)"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Исключение при создании проекта: {str(e)}"
        }

def get_chat_project(chat_id: str) -> str:
    """Получает текущий проект для чата из session_state.json"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("chat_projects", {}).get(chat_id)
    except Exception:
        pass
    return None