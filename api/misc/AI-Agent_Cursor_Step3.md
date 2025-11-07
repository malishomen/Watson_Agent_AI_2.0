# Cursor — Шаг 3: FastAPI‑режим агента + Telegram‑оператор (полный пакет)
> **Цель:** агент становится «живым» сервисом (FastAPI) с удалённым управлением через Telegram. Мы (МОЗГ) формируем ТЗ, отдаём команды; агент (ИСПОЛНИТЕЛЬ) выполняет всё «под ключ» с безопасностью и журналами.  
> **Предпосылки:** шаги 1–2 уже внедрены (SQLite‑память, /run /read /write /kill /cd /pwd /approve, WORKDIR‑постоянство, ProjectSpec.yml, run_project.py).

---

## 0) Состав пакета

Появятся новые файлы:
```
D:\\AI-Agent\\
├─ Memory\\GPT+Deepseek_Agent_memory.py         # ядро (уже есть)
├─ run_project.py                                # исполнитель YAML (уже есть)
├─ api\\fastapi_agent.py                         # НОВОЕ: HTTP API для агента
├─ bot\\telegram_operator.py                     # НОВОЕ: Telegram-оператор
├─ .env.example                                  # НОВОЕ: образец окружения
└─ cursor\\tasks.code.json                       # дополним задачами
```

Новые зависимости (в venv):
```powershell
pip install fastapi uvicorn python-telegram-bot==21.6 pyyaml
```

---

## 1) Переменные окружения (.env / setx)

### .env.example (создайте `D:\\AI-Agent\\.env.example`)
```env
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=deepseek-r1-distill-qwen-14b-abliterated-v2
OPENAI_API_KEY=sk-...

AGENT_DB=D:\\AI-Agent\\Memory\\agent_memory.sqlite
AGENT_WORKDIR=D:\\AI-Agent\\Memory

AGENT_HTTP_HOST=127.0.0.1
AGENT_HTTP_PORT=8088
AGENT_HTTP_SHARED_SECRET=change_me_long_random

TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
TELEGRAM_ADMIN_USER_ID=123456789

LOG_LEVEL=info
```

> На Windows можно задать через `setx` или хранить `.env` и грузить его из кода.

---

## 2) FastAPI сервис — `api/fastapi_agent.py`

**Назначение:** постоянный процесс, который:
- принимает команды (`/command`), чат (`/chat`), approvals (`/approve/:id`),
- проксирует в ядро: возвращает результат и логирует,
- проверяет авторизацию по `AGENT_HTTP_SHARED_SECRET`,
- даёт `GET /health`, `GET /workdir`, `POST /cd`,
- умеет запускать ProjectSpec: `POST /run-spec`.

Создайте `D:\\AI-Agent\\api\\fastapi_agent.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, subprocess
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
AGENT = str(ROOT / "Memory" / "GPT+Deepseek_Agent_memory.py")
RUNNER = str(ROOT / "run_project.py")

HOST = os.getenv("AGENT_HTTP_HOST", "127.0.0.1")
PORT = int(os.getenv("AGENT_HTTP_PORT", "8088"))
SHARED = os.getenv("AGENT_HTTP_SHARED_SECRET", "change_me")

DEFAULT_SESSION = "Danil-PC"

def check_auth(secret: Optional[str]):
    if not secret or secret != SHARED:
        raise HTTPException(status_code=401, detail="Unauthorized")

def call_agent(session: str, command: str) -> dict:
    cmd = ["python", AGENT, "--session", session, "--once", command]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"stdout": (p.stdout or "").strip(), "stderr": (p.stderr or "").strip(), "returncode": p.returncode}

def run_spec(spec_path: str) -> dict:
    cmd = ["python", RUNNER, spec_path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"stdout": (p.stdout or "").strip(), "stderr": (p.stderr or "").strip(), "returncode": p.returncode}

app = FastAPI(title="AI-Agent API", version="1.0.0")

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

@app.get("/health")
def health():
    return {"status": "ok"}

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

# запуск: uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
```

**Запуск сервера (в venv):**
```powershell
uvicorn api.fastapi_agent:app --host $env:AGENT_HTTP_HOST --port $env:AGENT_HTTP_PORT --reload
```
Если переменные не заданы, можно:
```powershell
uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
```
**Проверка:**
```powershell
curl http://127.0.0.1:8088/health
curl -X GET http://127.0.0.1:8088/workdir -H "x-agent-secret: change_me_long_random"
```

---

## 3) Telegram‑оператор — `bot/telegram_operator.py`

Создайте `D:\\AI-Agent\\bot\\telegram_operator.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, logging, asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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
    async with session.get(f"{API_URL}{path}", headers={"x-agent-secret": SECRET}) as r:
        return await r.json()

async def api_post(session: aiohttp.ClientSession, path: str, payload: dict):
    async with session.post(f"{API_URL}{path}", headers={"x-agent-secret": SECRET}, json=payload) as r:
        return await r.json()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    await update.message.reply_text("Готов к работе. /ping, /pwd, /cd <path>, /cmd <текст>, /approve <ID>, /run_spec <path>")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    async with aiohttp.ClientSession() as s:
        data = await api_get(s, "/health")
    await update.message.reply_text(f"API: {data}")

async def pwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    async with aiohttp.ClientSession() as s:
        data = await api_get(s, "/workdir")
    await update.message.reply_text(f"{data.get('stdout','')}")

async def cd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    if not context.args:
        await update.message.reply_text("Синтаксис: /cd D:\\путь")
        return
    path = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/cd", {"session": SESSION_DEFAULT, "path": path})
    await update.message.reply_text(data.get("stdout","") or data.get("stderr",""))

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    if not context.args:
        await update.message.reply_text("Синтаксис: /cmd <команда либо обычный запрос>")
        return
    command = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/command", {"session": SESSION_DEFAULT, "command": command})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(пусто)")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if str(uid) != str(ADMIN):
        await update.message.reply_text("Только админ может подтверждать.")
        return
    if not context.args:
        await update.message.reply_text("Синтаксис: /approve AP-123456789")
        return
    approval_id = context.args[0]
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/approve", {"session": SESSION_DEFAULT, "approval_id": approval_id})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(пусто)")

async def run_spec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_allowed(uid):
        await update.message.reply_text("Доступ запрещён.")
        return
    if not context.args:
        await update.message.reply_text("Синтаксис: /run_spec D:\\AI-Agent\\ProjectSpec.yml")
        return
    spec = " ".join(context.args)
    async with aiohttp.ClientSession() as s:
        data = await api_post(s, "/run-spec", {"spec_path": spec})
    out = data.get("stdout","") or data.get("stderr","")
    await update.message.reply_text(out[:4000] if out else "(пусто)")

async def main():
    if not BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN не задан")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("pwd", pwd))
    app.add_handler(CommandHandler("cd", cd))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("run_spec", run_spec))
    await app.initialize()
    await app.start()
    logging.info("Telegram operator started")
    await app.updater.start_polling(drop_pending_updates=True)
    await app.idle()

if __name__ == "__main__":
    import asyncio as _a
    _a.run(main())
```

---

## 4) Cursor — задачи (добавить в `cursor/tasks.code.json`)

```json
{
  "title": "API: start server",
  "description": "Запуск FastAPI сервиса агента (локально)",
  "steps": [
    { "type": "terminal", "command": "pip install fastapi uvicorn python-telegram-bot==21.6 pyyaml" },
    { "type": "terminal", "command": "uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload" }
  ]
},
{
  "title": "Bot: start telegram operator",
  "description": "Запуск Telegram-оператора (polling)",
  "steps": [
    { "type": "terminal", "command": "python bot/telegram_operator.py" }
  ]
},
{
  "title": "API: smoke test",
  "description": "Проверка API эндпоинтов",
  "steps": [
    { "type": "terminal", "command": "curl http://127.0.0.1:8088/health" },
    { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/workdir' -Headers @{ 'x-agent-secret'='change_me_long_random' } -Method GET | Select-Object -Expand Content" }
  ]
},
{
  "title": "Bot: smoke test",
  "description": "Проверка команд бота в чате",
  "steps": [
    { "type": "note", "content": "В Telegram: /start, затем /ping, /pwd, /cd D\\AI-Agent\\Memory, /cmd /notes" }
  ]
},
{
  "title": "Project: run via API from Cursor",
  "description": "Запуск ProjectSpec.yml через HTTP API",
  "steps": [
    { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/run-spec' -Headers @{ 'x-agent-secret'='change_me_long_random' } -Method POST -Body (@{spec_path='D:\\AI-Agent\\ProjectSpec.yml'} | ConvertTo-Json) -ContentType 'application/json' | Select-Object -Expand Content" }
  ]
}```

---

## 5) Безопасность и роли

- API требует заголовок `x-agent-secret`.
- Telegram доступ ограничен `TELEGRAM_ALLOWED_USER_IDS`; подтверждать может только `TELEGRAM_ADMIN_USER_ID`.
- Ядро уже применяет белые списки директорий и систему `/approve`.
- Логи: `D:\\AI-Agent\\Memory\\ops_log.csv`.

## 6) Быстрый чек‑лист

- [ ] `pip install fastapi uvicorn python-telegram-bot==21.6 pyyaml`
- [ ] Создать `api/fastapi_agent.py`, `bot/telegram_operator.py`, задать переменные окружения.
- [ ] Запустить API → проверить `/health` и `/workdir` с секретом.
- [ ] Запустить бота → проверить `/start`, `/pwd`, `/cd`, `/cmd`, `/run_spec`.
- [ ] Прогнать `ProjectSpec.yml` через API и через бота.
- [ ] Убедиться, что approvals работают, и всё логируется.

