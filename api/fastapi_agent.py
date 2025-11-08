from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
import json, time, urllib.request, urllib.error
import subprocess, os, shlex

from . import agent
from tools.llm_client import chat
from tools.patcher import apply_patch
from tools.tester import run_tests
from utils.prompts import SYSTEM_PATCH_PROMPT, USER_PATCH_TEMPLATE
from utils.router_core import plan_and_route, do_project_create, get_chat_project
import requests
try:
    import tomllib
except Exception:
    tomllib = None

app = FastAPI(title="Watson Agent API")
START_TS = time.time()

# Глобальный обработчик ошибок
@app.exception_handler(Exception)
def all_exceptions_handler(request, exc):
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})


class RespondIn(BaseModel):
    message: str
    user_id: Optional[int] = None
    ctx: Optional[dict[str, Any]] = None


class RespondOut(BaseModel):
    ok: bool
    reply: str


@app.get("/")
def root():
    return {"status": "ok", "service": "watson-agent", "uptime_sec": round(time.time() - START_TS, 1)}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/metrics")
def metrics():
    """Метрики системы для мониторинга (V3 расширенная)"""
    import glob
    import subprocess
    from pathlib import Path
    
    inbox_path = Path(__file__).parent.parent / "inbox"
    inbox_count = len(glob.glob(str(inbox_path / "*.task.json"))) if inbox_path.exists() else 0
    
    # Версия из конфига
    version_info = version()
    
    # Git SHA (V3)
    git_sha = os.getenv("GIT_SHA", "unknown")
    if git_sha == "unknown":
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                git_sha = result.stdout.strip()
        except:
            pass
    
    # Профиль (V3)
    try:
        from utils.profile_loader import get_current_profile
        profile_data = get_current_profile()
        profile_name = profile_data.get("environment", os.getenv("WATSON_PROFILE", "local"))
        registry_url = profile_data.get("registry", "unknown")
        registry_ns = profile_data.get("registry_namespace", "unknown")
    except:
        profile_name = os.getenv("WATSON_PROFILE", "local")
        registry_url = os.getenv("REGISTRY_URL", "unknown")
        registry_ns = os.getenv("REGISTRY_NS", "unknown")
    
    # Image tags (V3)
    image_tag = os.getenv("IMAGE_TAG", "unknown")
    project_slug = os.path.basename(os.getcwd()).lower().replace(" ", "_")
    
    backend_image = f"{registry_url}/{registry_ns}/{project_slug}_backend:{image_tag}" if registry_url != "unknown" else "unknown"
    frontend_image = f"{registry_url}/{registry_ns}/{project_slug}_frontend:{image_tag}" if registry_url != "unknown" else "unknown"
    
    # Активный проект
    active_project = "unknown"
    try:
        from utils.router_core import get_chat_project
        active_project = "n/a"
    except:
        pass
    
    # Статус watcher
    watcher_running = False
    try:
        import psutil
        for proc in psutil.process_iter(['name', 'cmdline']):
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if 'task_watcher' in cmdline:
                    watcher_running = True
                    break
    except:
        pass
    
    return {
        "uptime_sec": round(time.time() - START_TS, 1),
        "version": {
            **version_info,
            "git_sha": git_sha,
            "image_tag": image_tag
        },
        "images": {
            "backend": backend_image,
            "frontend": frontend_image
        },
        "profile": {
            "active": profile_name,
            "registry": registry_url
        },
        "inbox_queue": inbox_count,
        "active_project": active_project,
        "watcher_running": watcher_running,
        "timestamp": time.time()
    }


@app.get("/version")
def version():
    try:
        if tomllib and os.path.exists("config.toml"):
            cfg = tomllib.load(open("config.toml", "rb"))
        else:
            cfg = {}
    except Exception:
        cfg = {}
    models = cfg.get("models", {})
    return {
        "service": "watson-agent",
        "uptime_sec": round(time.time() - START_TS, 1),
        "reasoning_model": models.get("reasoning_model"),
        "coder_model": models.get("coder_model"),
    }

# === Telegram helpers -------------------------------------------------------
def _tg_send(msg: str) -> bool:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg[:4000]},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


class BotCommandIn(BaseModel):
    text: str


@app.post("/bot/command")
def bot_command(body: BotCommandIn):
    if not body.text:
        raise HTTPException(status_code=400, detail="Нет текста команды")
    ok = _tg_send(f"📡 Принято: {body.text}")
    return {"ok": ok, "echo": body.text}


@app.post("/agent/respond", response_model=RespondOut)
def agent_respond(body: RespondIn):
    try:
        if body.user_id is None:
            reply = agent.respond(body.message, ctx=body.ctx)
        else:
            reply = agent.respond(body.user_id, body.message, ctx=body.ctx)
        return {"ok": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======== /autocode/generate =================================================
from pydantic import Field

class AutoCodeGenIn(BaseModel):
    task: str = Field(..., min_length=6)
    repo_path: Optional[str] = None
    test_cmd: Optional[str] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = 2048
    model: Optional[str] = None   # default from config models.coder_model
    dry_run: bool = False


class AutoCodeGenOut(BaseModel):
    ok: bool
    applied: bool
    tests_passed: Optional[bool]
    diff_len: int
    logs: str
    diff: Optional[str] = None


def _load_cfg():
    cfg_repo = os.getcwd()
    cfg_test = "pytest -q"
    cfg_models = {}
    try:
        if tomllib and os.path.exists("config.toml"):
            cfg = tomllib.load(open("config.toml", "rb"))
            cfg_repo = (cfg.get("repo_path") or cfg_repo).replace("/", "\\")
            cfg_test = cfg.get("test_cmd", cfg_test)
            cfg_models = cfg.get("models", {})
    except Exception:
        pass
    return cfg_repo, cfg_test, cfg_models


@app.post("/autocode/generate", response_model=AutoCodeGenOut)
def autocode_generate(body: AutoCodeGenIn):
    # Мягкая валидация задачи - принимаем описания проблем и баг-репорты
    coding_keywords = [
        # Действия
        'add', 'fix', 'refactor', 'test', 'implement', 'create', 'update', 'remove', 'change',
        'добав', 'созда', 'измен', 'удал', 'исправ', 'рефактор',
        # Проблемы и баги
        'bug', 'issue', 'problem', 'error', 'не работает', 'проблема', 'баг', 'ошибка',
        'просит', 'требует', 'запрашивает', 'каждый раз', 'логика не работает',
        # Технические термины
        'функци', 'модуль', 'компонент', 'auth', 'login', 'email', 'пин', 'код',
        'ссылк', 'вход', 'авториз', 'логин'
    ]
    
    # Минимальная длина задачи
    if len(body.task.strip()) < 10:
        raise HTTPException(status_code=400, 
                          detail="Задача слишком короткая. Опишите проблему подробнее.")
    
    # Если хотя бы одно ключевое слово найдено ИЛИ задача длинная (>30 символов)
    # - считаем её потенциально кодовой
    task_lower = body.task.lower()
    has_keyword = any(kw in task_lower for kw in coding_keywords)
    is_descriptive = len(body.task.strip()) > 30
    
    if not (has_keyword or is_descriptive):
        raise HTTPException(status_code=400, 
                          detail="Опишите задачу подробнее или укажите что нужно сделать.")
    
    repo_cfg, test_cfg, models_cfg = _load_cfg()
    repo = body.repo_path or repo_cfg
    test_cmd = body.test_cmd or test_cfg
    # Model selection: body.model > WATSON_DIFF_MODEL env > diff_generator > coder_model
    model_name = (body.model or 
                  os.environ.get("WATSON_DIFF_MODEL") or 
                  models_cfg.get("diff_generator") or 
                  models_cfg.get("coder_model"))
    if not model_name:
        raise HTTPException(400, "Diff generator model is not configured")

    messages = [
        {"role": "system", "content": SYSTEM_PATCH_PROMPT.strip()},
        {"role": "user", "content": USER_PATCH_TEMPLATE.format(repo=repo, task=body.task).strip()},
    ]
    reply = chat(model_name, messages, temperature=body.temperature, max_tokens=body.max_tokens)
    start = reply.find("```diff")
    end = reply.rfind("```")
    if start == -1 or end == -1 or end <= start:
        raise HTTPException(500, "Model did not return a diff fenced block")
    patch_text = reply[start + 7 : end].strip()

    if body.dry_run:
        _tg_send(f"🧪 DRY-RUN\nTask: {body.task}\nModel: {model_name}\nDiff: {len(patch_text)} bytes")
        return {"ok": True, "applied": False, "tests_passed": None, "diff_len": len(patch_text), "logs": "dry-run", "diff": patch_text}

    ok, out = apply_patch(repo, patch_text)
    logs = [out]
    if not ok:
        _tg_send(f"🧩 PATCH FAILED TO APPLY\nTask: {body.task}\nModel: {model_name}\nDiff: {len(patch_text)} bytes")
        return {"ok": True, "applied": False, "tests_passed": None, "diff_len": len(patch_text), "logs": "\n".join(logs), "diff": patch_text}

    passed, tlog = run_tests(repo, test_cmd)
    logs.append(tlog[:2000])
    _tg_send(
        "✅ PATCH APPLIED\n"
        f"Task: {body.task}\n"
        f"Model: {model_name}\n"
        f"Diff: {len(patch_text)} bytes\n"
        f"Tests: {'PASSED' if passed else 'FAILED'}"
    )
    return {"ok": True, "applied": True, "tests_passed": passed, "diff_len": len(patch_text), "logs": "\n".join(logs)}


# ======== /relay/submit - Единый роутер задач =================================
class RelaySubmitIn(BaseModel):
    text: str
    dry_run: bool = False
    chat_id: Optional[str] = None

class RelaySubmitOut(BaseModel):
    ok: bool
    intent: str
    response: Optional[str] = None
    project_name: Optional[str] = None
    project_path: Optional[str] = None
    diff: Optional[str] = None
    logs: Optional[str] = None
    error: Optional[str] = None

@app.post("/relay/submit", response_model=RelaySubmitOut)
def relay_submit(body: RelaySubmitIn):
    """
    Универсальный endpoint для обработки задач.
    Принимает текст, определяет intent через DeepSeek, маршрутизирует.
    """
    try:
        print(f"[RELAY] Received: {body.text[:100]}...")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    try:
        # Определяем intent (без LLM клиента, используем простой роутер)
        route_result = plan_and_route(body.text, None)
        intent = route_result.get("intent", "unknown")
        
        try:
            print(f"[RELAY] Intent: {intent}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        
        # Обработка по intent
        if intent == "help":
            return RelaySubmitOut(
                ok=True,
                intent="help",
                response=route_result.get("response")
            )
        
        if intent == "ping":
            return RelaySubmitOut(
                ok=True,
                intent="ping",
                response=route_result.get("response")
            )
        
        if intent == "noncode":
            return RelaySubmitOut(
                ok=True,
                intent="noncode",
                response=route_result.get("response", "Это не кодовая задача")
            )
        
        if intent == "project_create":
            project_name = route_result.get("project_name")
            if not project_name:
                raise HTTPException(400, "Project name not specified")
            
            result = do_project_create(project_name)
            
            if result.get("success"):
                return RelaySubmitOut(
                    ok=True,
                    intent="project_create",
                    project_name=result.get("project_name"),
                    project_path=result.get("project_path"),
                    response=f"✅ Проект создан: {result.get('project_path')}"
                )
            else:
                return RelaySubmitOut(
                    ok=False,
                    intent="project_create",
                    error=result.get("error")
                )
        
        if intent == "code":
            # Определяем repo_path
            repo_cfg, test_cfg, models_cfg = _load_cfg()
            repo_path = get_chat_project(body.chat_id) or repo_cfg
            
            if not repo_path or not os.path.exists(repo_path):
                return RelaySubmitOut(
                    ok=False,
                    intent="code",
                    error=f"⚠️ Repo path not found or invalid: {repo_path}"
                )
            
            # Нормализованный текст задачи
            task_text = route_result.get("normalized_text", body.text)
            
            # Опция: делегация в Cursor С ПРЕДВАРИТЕЛЬНОЙ ГЕНЕРАЦИЕЙ ЧЕРЕЗ LLM
            use_cursor_delegation = os.getenv("WATSON_USE_CURSOR_DELEGATION", "false").lower() == "true"
            
            if use_cursor_delegation:
                # ОПТИМИЗИРОВАННАЯ ЛОГИКА: Используем только Qwen для быстрой генерации
                try:
                    import random
                    from pathlib import Path
                    
                    # ШАГ 1: Qwen 2.5 Coder анализирует и генерирует diff (быстро!)
                    print(f"[RELAY] Qwen 2.5 Coder: analyzing and generating diff...")
                    gen_body = AutoCodeGenIn(
                        task=task_text,
                        repo_path=repo_path,
                        dry_run=True  # Всегда dry-run для делегации
                    )
                    gen_result = autocode_generate(gen_body)
                    
                    diff_data = gen_result.get("diff") if isinstance(gen_result, dict) else getattr(gen_result, "diff", None)
                    
                    if not diff_data:
                        raise ValueError("No diff generated by Qwen")
                    
                    print(f"[RELAY] Qwen generated diff: {len(diff_data)} bytes")
                    
                    # ШАГ 2: Создаем задачу для Cursor с готовым diff
                    inbox_dir = Path(__file__).parent.parent / "inbox"
                    inbox_dir.mkdir(exist_ok=True)
                    
                    task_id = random.randint(1000, 9999)
                    task_file = inbox_dir / f"task_{task_id}.task.json"
                    
                    task_data = {
                        "text": task_text,
                        "repo_path": repo_path,
                        "dry_run": body.dry_run,
                        "chat_id": body.chat_id or "api",
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        # КЛЮЧЕВОЕ: передаем готовый diff от Qwen
                        "llm_analysis": f"Generated by Qwen 2.5 Coder",
                        "generated_diff": diff_data,
                        "action": "apply_diff"  # Cursor должен применить готовый diff
                    }
                    
                    with open(task_file, "w", encoding="utf-8") as f:
                        json.dump(task_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"[RELAY] Task created for Cursor: task_{task_id}")
                    
                    return RelaySubmitOut(
                        ok=True,
                        intent="code",
                        response=f"✅ Qwen 2.5 обработал задачу!\n\n📝 Diff: {len(diff_data)} bytes\n\n📋 Задача для Cursor: task_{task_id}\n🎯 Откройте cursor_tasks/task_{task_id}_instruction.md",
                        diff=diff_data
                    )
                except Exception as e:
                    # Fallback на обычную генерацию
                    print(f"[RELAY] Cursor delegation failed: {e}, using direct execution")
                    use_cursor_delegation = False  # Переключаемся на прямое выполнение
            
            # Вызываем /autocode/generate напрямую (без Cursor)
            if not use_cursor_delegation:
                try:
                    gen_body = AutoCodeGenIn(
                        task=task_text,
                        repo_path=repo_path,
                        dry_run=body.dry_run
                    )
                    gen_result = autocode_generate(gen_body)
                    
                    # gen_result это dict, не объект
                    tests_status = gen_result.get("tests_passed") if isinstance(gen_result, dict) else getattr(gen_result, "tests_passed", None)
                    diff_data = gen_result.get("diff") if isinstance(gen_result, dict) else getattr(gen_result, "diff", None)
                    logs_data = gen_result.get("logs") if isinstance(gen_result, dict) else getattr(gen_result, "logs", None)
                    
                    return RelaySubmitOut(
                        ok=True,
                        intent="code",
                        response=f"📂 Repo: {repo_path}\n{'🧪 DRY-RUN' if body.dry_run else '✅ Applied'}\nTests: {tests_status}",
                        diff=diff_data,
                        logs=logs_data
                    )
                except HTTPException as e:
                    return RelaySubmitOut(
                        ok=False,
                        intent="code",
                        error=f"Code generation failed: {e.detail}"
                    )
        
        # Unknown intent
        return RelaySubmitOut(
            ok=False,
            intent=intent,
            error=f"Unknown intent: {intent}"
        )
        
    except Exception as e:
        try:
            print(f"[RELAY] Error: {e}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        return RelaySubmitOut(
            ok=False,
            intent="error",
            error=str(e)
        )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, subprocess
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
AGENT = str(ROOT / "Memory" / "GPT+Deepseek_Agent_memory.py")
RUNNER = str(ROOT / "run_project.py")

HOST = os.getenv("AGENT_HTTP_HOST", "127.0.0.1")
PORT = int(os.getenv("AGENT_HTTP_PORT", "8088"))
SHARED = os.getenv("AGENT_HTTP_SHARED_SECRET", "change_me")

DEFAULT_SESSION = "Danil-PC"

def check_auth(secret: Optional[str]):
    expected = os.getenv("AGENT_HTTP_SHARED_SECRET", "").strip()
    got = (secret or "").strip()
    print(f"[DEBUG] expected=<{expected}> (len={len(expected)}), got=<{got}> (len={len(got)})")
    if got != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

def _utf8_env():
    env = os.environ.copy()
    # РіР°СЂР°РЅС‚РёСЂСѓРµРј UTF-8 РІ РґРѕС‡РµСЂРЅРµРј РїСЂРѕС†РµСЃСЃРµ Python
    env["PYTHONIOENCODING"] = "utf-8"
    env["CHCP"] = "65001"  # РґР»СЏ РЅРµРєРѕС‚РѕСЂС‹С… СЃС†РµРЅР°СЂРёРµРІ Windows РєРѕРЅСЃРѕР»Рё
    return env

def _mask_sensitive_data(text: str) -> str:
    """РњР°СЃРєРёСЂСѓРµС‚ С‡СѓРІСЃС‚РІРёС‚РµР»СЊРЅС‹Рµ РґР°РЅРЅС‹Рµ РІ Р»РѕРіР°С…"""
    import re
    # РњР°СЃРєРёСЂСѓРµРј С‚РѕРєРµРЅС‹, РєР»СЋС‡Рё API Рё РґСЂСѓРіРёРµ С‡СѓРІСЃС‚РІРёС‚РµР»СЊРЅС‹Рµ РґР°РЅРЅС‹Рµ
    text = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***MASKED***', text)
    text = re.sub(r'[0-9]+:[A-Za-z0-9_-]{35}', '***BOT_TOKEN_MASKED***', text)
    text = re.sub(r'AP-[0-9]+', 'AP-***MASKED***', text)
    return text

def call_agent(session: str, command: str) -> dict:
    cmd = ["python", AGENT, "--session", session, "--once", command]
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",          # рџ‘€ РєР»СЋС‡РµРІРѕР№ РјРѕРјРµРЅС‚
        env=_utf8_env(),           # рџ‘€ Рё РІРѕС‚ СЌС‚Рѕ
    )
    # РњР°СЃРєРёСЂСѓРµРј С‡СѓРІСЃС‚РІРёС‚РµР»СЊРЅС‹Рµ РґР°РЅРЅС‹Рµ РІ РІС‹РІРѕРґРµ
    stdout_masked = _mask_sensitive_data(p.stdout or "")
    stderr_masked = _mask_sensitive_data(p.stderr or "")
    
    return {
        "stdout": stdout_masked.strip(), 
        "stderr": stderr_masked.strip(), 
        "returncode": p.returncode
    }

def run_spec(spec_path: str) -> dict:
    cmd = ["python", RUNNER, spec_path]
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",          # рџ‘€
        env=_utf8_env(),           # рџ‘€
    )
    # РњР°СЃРєРёСЂСѓРµРј С‡СѓРІСЃС‚РІРёС‚РµР»СЊРЅС‹Рµ РґР°РЅРЅС‹Рµ РІ РІС‹РІРѕРґРµ
    stdout_masked = _mask_sensitive_data(p.stdout or "")
    stderr_masked = _mask_sensitive_data(p.stderr or "")
    
    return {
        "stdout": stdout_masked.strip(), 
        "stderr": stderr_masked.strip(), 
        "returncode": p.returncode
    }

class CmdBody(BaseModel):
    session: Optional[str] = DEFAULT_SESSION
    command: str

class ChatBody(BaseModel):
    session: Optional[str] = DEFAULT_SESSION
    text: str

class ApproveBody(BaseModel):
    session: Optional[str] = DEFAULT_SESSION
    approval_id: str

class CdBody(BaseModel):
    session: Optional[str] = DEFAULT_SESSION
    path: str

class SpecBody(BaseModel):
    spec_path: str

# Cursor API proxy models
class OpenReq(BaseModel):
    filepath: str

class InsertReq(BaseModel):
    filepath: str
    position: str
    text: str

class ReplaceReq(BaseModel):
    filepath: str
    range: str
    text: str

class TerminalReq(BaseModel):
    cwd: str
    command: str

class TaskReq(BaseModel):
    task_id: str
    params: dict | None = None

class ChatReq(BaseModel):
    prompt: str

def get_cursor_client():
    try:
        from api.misc.cursor_bridge.cursor_client import CursorClient
        return CursorClient()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Cursor bridge not available: {str(e)}")

def require_secret(x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)

# note: /health is already defined above for this app

@app.get("/workdir")
def get_workdir(x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    r = call_agent(DEFAULT_SESSION, "/pwd")
    return r

@app.post("/cd")
def api_cd(body: CdBody, x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    r = call_agent(body.session or DEFAULT_SESSION, f"/cd {body.path}")
    return r

@app.post("/command")
def api_command(body: CmdBody, x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    r = call_agent(body.session or DEFAULT_SESSION, body.command)
    return r

@app.post("/chat")
def api_chat(body: ChatBody, x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    text = body.text.strip()
    if not text:
        raise HTTPException(400, "empty text")
    r = call_agent(body.session or DEFAULT_SESSION, text)
    return r

@app.post("/approve")
def api_approve(body: ApproveBody, x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    r = call_agent(body.session or DEFAULT_SESSION, f"/approve {body.approval_id}")
    return r

@app.post("/run-spec")
def api_run_spec(body: SpecBody, x_agent_secret: Optional[str] = Header(None)):
    check_auth(x_agent_secret)
    if not Path(body.spec_path).exists():
        raise HTTPException(404, f"Spec not found: {body.spec_path}")
    r = run_spec(body.spec_path)
    return r

# Cursor API proxy endpoints
@app.post("/cursor/open")
def cursor_open(req: OpenReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.open_file(req.filepath)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/insert")
def cursor_insert(req: InsertReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.insert(req.filepath, req.position, req.text)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/replace")
def cursor_replace(req: ReplaceReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.replace(req.filepath, req.range, req.text)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/save")
def cursor_save(req: OpenReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.save(req.filepath)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/create")
def cursor_create(req: InsertReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.create(req.filepath, req.text)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/terminal")
def cursor_terminal(req: TerminalReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.run_terminal(req.cwd, req.command)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/task")
def cursor_task(req: TaskReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.run_task(req.task_id, req.params or {})
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/chat")
def cursor_chat(req: ChatReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.chat(req.prompt)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

@app.post("/cursor/project")
def cursor_project(req: OpenReq, auth: None = Depends(require_secret)):
    try:
        client = get_cursor_client()
        return client.open_project(req.filepath)
    except Exception as e:
        return {"error": f"Cursor API not configured: {str(e)}", "status": 503}

# ===== РќРѕРІС‹Р№ СѓРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Р№ endpoint /command =====
from api.parsers.nlp_command_router import parse_free_text

class CommandIn(BaseModel):
    text: str
    session: str | None = "Telegram"   # РјРѕР¶РЅРѕ РїРµСЂРµРґР°РІР°С‚СЊ chat_id/username
    mode: str | None = None            # future: "agent"/"terminal"/"cursor"

class CommandOut(BaseModel):
    ok: bool
    normalized: str
    result: str

@app.post("/parse-command", response_model=CommandOut)
def parse_command_endpoint(payload: CommandIn, x_agent_secret: Optional[str] = Header(None)):
    """
    РџСЂРёРЅРёРјР°РµС‚ РїСЂРѕРёР·РІРѕР»СЊРЅС‹Р№ С‚РµРєСЃС‚ в†’ РЅРѕСЂРјР°Р»РёР·СѓРµС‚ в†’ РіРѕРЅРёС‚ РІ respond(...)
    """
    check_auth(x_agent_secret)
    
    user_text = payload.text or ""
    session = payload.session or "Telegram"
    
    # Р•СЃР»Рё С‚РµРєСЃС‚ СѓР¶Рµ slash-РєРѕРјР°РЅРґР° вЂ” РѕСЃС‚Р°РІР»СЏРµРј, РёРЅР°С‡Рµ РїР°СЂСЃРёРј
    normalized = user_text if user_text.strip().startswith("/") else parse_free_text(user_text)
    
    try:
        result = call_agent(session, normalized)
        if result.get("ok"):
            return CommandOut(ok=True, normalized=normalized, result=result.get("output", ""))
        else:
            return CommandOut(ok=False, normalized=normalized, result=result.get("error", "Unknown error"))
    except Exception as e:
        return CommandOut(ok=False, normalized=normalized, result=f"РћСЃС€РёР±РєР°: {e}")

# ===================== OPS: SMOKE =====================
class SmokeReq(BaseModel):
    host: str
    timeout: int = 60

def _http_get_json(url: str, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8", errors="replace")
        return json.loads(data)

@app.post("/ops/smoke")
def ops_smoke(req: SmokeReq):
    """
    Лёгкий smoke чек staging-сервиса:
      1) GET http://host:8080/health -> {"ok": true}
      2) GET http://host:8080/metrics -> содержит version.git_sha, version.image_tag, profile.active="staging"
    Возвращает краткий отчёт или HTTP 502 при фейле.
    """
    start = time.monotonic()
    base = f"http://{req.host}:8080"
    try:
        health = _http_get_json(f"{base}/health", timeout=req.timeout)
        if not isinstance(health, dict) or not health.get("ok"):
            raise RuntimeError("health != ok:true")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"/health failed: {e}")

    try:
        metrics = _http_get_json(f"{base}/metrics", timeout=req.timeout)
        ver = (metrics or {}).get("version") or {}
        prof = (metrics or {}).get("profile") or {}
        git_sha = ver.get("git_sha")
        image_tag = ver.get("image_tag")
        active = prof.get("active")
        if not git_sha or not image_tag or active != "staging":
            raise RuntimeError("metrics fields missing or profile.active!=staging")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"/metrics failed: {e}")

    dur = round(time.monotonic() - start, 3)
    return {
        "ok": True,
        "host": req.host,
        "image_tag": image_tag,
        "git_sha": git_sha,
        "duration_sec": dur,
    }

# ===================== OPS: DEPLOY / PROMOTE / ROLLBACK =====================
class DeployReq(BaseModel):
    host: str
    ref: str = "main"
    timeout: int = 120

class PromoteReq(BaseModel):
    host: str
    tag: str
    timeout: int = 120

class RollbackReq(BaseModel):
    host: str
    to: str = "prev"   # prev | <tag>
    timeout: int = 120

def _run_pwsh(script_path: str, args: list[str], timeout: int) -> dict:
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"script not found: {script_path}")
    cmd = ["pwsh", "-NoProfile", "-File", script_path] + args
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}

@app.post("/ops/deploy")
def ops_deploy(req: DeployReq):
    """
    Стейджинг-деплой:
      - сборка/пуш образов (делает CI заранее — тут идемпо Ansible Pull)
      - ansible/compose на хосте
    """
    try:
        res = _run_pwsh(
            os.path.join("scripts", "StagingDeploy.ps1"),
            ["-Host", req.host, "-Ref", req.ref, "-TimeoutSec", str(req.timeout)],
            timeout=req.timeout + 20,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"deploy error: {e}")
    ok = (res["returncode"] == 0)
    if not ok:
        raise HTTPException(status_code=502, detail=res["stderr"] or res["stdout"] or "deploy failed")
    return {"ok": True, "host": req.host, "ref": req.ref, "output": res["stdout"]}

@app.post("/ops/promote")
def ops_promote(req: PromoteReq):
    """Продвижение готового образа (tag) на staging."""
    try:
        res = _run_pwsh(
            os.path.join("scripts", "PromoteTag.ps1"),
            ["-Host", req.host, "-Tag", req.tag, "-TimeoutSec", str(req.timeout)],
            timeout=req.timeout + 20,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"promote error: {e}")
    if res["returncode"] != 0:
        raise HTTPException(status_code=502, detail=res["stderr"] or res["stdout"] or "promote failed")
    return {"ok": True, "host": req.host, "tag": req.tag, "output": res["stdout"]}

@app.post("/ops/rollback")
def ops_rollback(req: RollbackReq):
    """Откат версии: to=prev или to=<tag>."""
    try:
        res = _run_pwsh(
            os.path.join("scripts", "Rollback.ps1"),
            ["-Host", req.host, "-To", req.to, "-TimeoutSec", str(req.timeout)],
            timeout=req.timeout + 20,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"rollback error: {e}")
    if res["returncode"] != 0:
        raise HTTPException(status_code=502, detail=res["stderr"] or res["stdout"] or "rollback failed")
    return {"ok": True, "host": req.host, "to": req.to, "output": res["stdout"]}

# Р·Р°РїСѓСЃРє: uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
