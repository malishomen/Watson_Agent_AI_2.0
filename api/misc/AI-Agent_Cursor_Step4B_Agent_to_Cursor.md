# STEP 4B — Agent → Cursor API (обратное управление: **АГЕНТ управляет Cursor**)

> **Задача:** из вашего локального агента вызывать **Cursor API** для действий в редакторе: открывать/создавать файлы, вставлять/редактировать текст, запускать терминал, триггерить Chat/Autocomplete и Run Task.  
> **Важно:** ниже — универсальная обвязка с *настраиваемой картой эндпоинтов*. Если у вас уже есть спецификация Cursor API — просто пропишите точные пути/методы/поля в `cursor_api_map.json` (см. §2).

---

## 0) Предпосылки

- Агент запущен: `uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088`  
- У вас **есть** `CURSOR_API_URL` и `CURSOR_API_KEY` (или аналогичный токен).  
- Python 3.11+, requests установлен в venv.

Структура проекта (добавим папку и файлы):
```
D:\AI-Agent
├─ api\fastapi_agent.py ← добавим прокси-эндпоинты /cursor/*
├─ cursor_bridge\ ← НОВОЕ
│ ├─ cursor_client.py ← универсальный клиент
│ ├─ cursor_api_map.json ← карта действий → эндпоинты
│ └─ examples\payloads*.json ← примеры тел/ответов (опц.)
├─ ProjectSpec.yml ← добавим шаги /cursor:*
└─ scripts\
└─ cursor_proxy_tests.ps1 ← быстрая проверка
```

---

## 1) Переменные окружения (один раз на сессию)

Откройте PowerShell (внутри venv или рядом) и задайте:
```powershell
$env:CURSOR_API_URL="http://127.0.0.1:7007"    # пример, замените на ваш
$env:CURSOR_API_KEY="PASTE-YOUR-CURSOR-TOKEN"  # пример, замените на ваш
```

Если у вас другой тип аутентификации (Bearer, custom header, cookie) — это настраивается в cursor_api_map.json (§2).

---

## 2) Карта эндпоинтов: cursor_bridge/cursor_api_map.json

Создайте файл и опишите реальные пути вашего API. Ниже — ШАБЛОН (замените path, method, auth и payload под вашу спецификацию).

```json
{
  "$schema": "https://example.local/cursor-map.schema.json",
  "auth": {
    "type": "header",                     // header | bearer | cookie | none
    "header_name": "Authorization",       // если type=header
    "format": "Bearer {token}"            // как вставлять ключ
  },
  "endpoints": {
    "editor.open":  { "method": "POST", "path": "/v1/editor/open" },
    "editor.insert":{ "method": "POST", "path": "/v1/editor/insert" },
    "editor.replace":{"method": "POST", "path": "/v1/editor/replace" },
    "editor.save":  { "method": "POST", "path": "/v1/editor/save" },
    "files.create": { "method": "POST", "path": "/v1/files/create" },
    "terminal.run": { "method": "POST", "path": "/v1/terminal/run" },
    "task.run":     { "method": "POST", "path": "/v1/tasks/run" },
    "chat.prompt":  { "method": "POST", "path": "/v1/chat/complete" },
    "project.open": { "method": "POST", "path": "/v1/workspace/open" }
  },
  "payload_templates": {
    "editor.open":   { "filepath": "{filepath}", "create_if_missing": true },
    "editor.insert": { "filepath": "{filepath}", "position": "{position}", "text": "{text}" },
    "editor.replace":{ "filepath": "{filepath}", "range": "{range}", "text": "{text}" },
    "editor.save":   { "filepath": "{filepath}" },
    "files.create":  { "filepath": "{filepath}", "text": "{text}" },
    "terminal.run":  { "cwd": "{cwd}", "command": "{command}", "timeout_sec": 120 },
    "task.run":      { "task_id": "{task_id}", "params": "{params}" },
    "chat.prompt":   { "messages": [{ "role": "user", "content": "{prompt}" }], "stream": false },
    "project.open":  { "root": "{root}" }
  }
}
```

> **✍️ Совет:** добавьте сюда настоящие пути и имена полей из вашей Cursor API. Тогда остальной код заработает без правок.

---

## 3) Универсальный клиент: cursor_bridge/cursor_client.py

```python
# cursor_bridge/cursor_client.py
from __future__ import annotations
import os, json, time
from typing import Any, Dict
import requests

class CursorClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, map_path: str | None = None):
        self.base_url = base_url or os.environ.get("CURSOR_API_URL", "").rstrip("/")
        self.token = token or os.environ.get("CURSOR_API_KEY", "")
        self.map = self._load_map(map_path or os.path.join(os.path.dirname(__file__), "cursor_api_map.json"))
        self._auth_hdr_name, self._auth_fmt = self._parse_auth(self.map.get("auth", {}))

    @staticmethod
    def _load_map(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _parse_auth(auth: Dict[str, Any]):
        t = auth.get("type", "none")
        if t == "header":
            return auth.get("header_name", "Authorization"), auth.get("format", "Bearer {token}")
        return None, None  # bearer/cookie можно расширить при необходимости

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._auth_hdr_name and self.token:
            h[self._auth_hdr_name] = self._auth_fmt.format(token=self.token)
        return h

    def call(self, action: str, **kwargs) -> Dict[str, Any]:
        ep = self.map["endpoints"].get(action)
        if not ep: 
            raise KeyError(f"Unknown action: {action}")
        path = ep["path"]
        method = ep.get("method", "POST").upper()
        url = f"{self.base_url}{path}"
        template = (self.map.get("payload_templates", {}).get(action) or {})
        payload = json.loads(json.dumps(template).format(**{k: json.dumps(v)[1:-1] if isinstance(v, (dict, list)) else v for k,v in kwargs.items()}))
        resp = requests.request(method, url, headers=self._headers(), json=payload, timeout=120)
        try:
            data = resp.json()
        except Exception:
            data = {"text": resp.text}
        return {"status": resp.status_code, "data": data, "ok": resp.ok}

    # Sugar helpers
    def open_file(self, filepath: str):          return self.call("editor.open", filepath=filepath)
    def insert(self, filepath: str, position: str, text: str): return self.call("editor.insert", filepath=filepath, position=position, text=text)
    def replace(self, filepath: str, range: str, text: str):   return self.call("editor.replace", filepath=filepath, range=range, text=text)
    def save(self, filepath: str):               return self.call("editor.save", filepath=filepath)
    def create(self, filepath: str, text: str):  return self.call("files.create", filepath=filepath, text=text)
    def run_terminal(self, cwd: str, command: str): return self.call("terminal.run", cwd=cwd, command=command)
    def run_task(self, task_id: str, params: dict | None = None): return self.call("task.run", task_id=task_id, params=params or {})
    def chat(self, prompt: str):                 return self.call("chat.prompt", prompt=prompt)
    def open_project(self, root: str):           return self.call("project.open", root=root)
```

---

## 4) Прокси-роуты в вашем агенте (api/fastapi_agent.py)

Добавьте рядом с существующими эндпоинтами защищённые маршруты /cursor/* (используем тот же x-agent-secret).

```python
# Вставьте в api/fastapi_agent.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from cursor_bridge.cursor_client import CursorClient

router = APIRouter(prefix="/cursor", tags=["cursor"])

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

def get_client() -> CursorClient:
    return CursorClient()

@router.post("/open")
def cursor_open(req: OpenReq, auth: None = Depends(require_secret)):
    return get_client().open_file(req.filepath)

@router.post("/insert")
def cursor_insert(req: InsertReq, auth: None = Depends(require_secret)):
    return get_client().insert(req.filepath, req.position, req.text)

@router.post("/replace")
def cursor_replace(req: ReplaceReq, auth: None = Depends(require_secret)):
    return get_client().replace(req.filepath, req.range, req.text)

@router.post("/terminal")
def cursor_terminal(req: TerminalReq, auth: None = Depends(require_secret)):
    return get_client().run_terminal(req.cwd, req.command)

@router.post("/task")
def cursor_task(req: TaskReq, auth: None = Depends(require_secret)):
    return get_client().run_task(req.task_id, req.params or {})

@router.post("/chat")
def cursor_chat(req: ChatReq, auth: None = Depends(require_secret)):
    return get_client().chat(req.prompt)
```

И подключите router к приложению (внизу файла, где подключены другие роутеры):

```python
from api.fastapi_agent import app  # или ваш путь к app
app.include_router(router)
```

> **⚠️ Вставки могут отличаться в зависимости от вашей структуры. Главное — маршруты /cursor/* защищены тем же секретом, что и остальной API агента.**

---

## 5) ProjectSpec.yml — новые шаги для управления Cursor

Добавьте шаги в ваш ProjectSpec.yml, чтобы агент мог сам нажимать на кнопки Cursor через API:

```yaml
steps:
  - name: "Open project in Cursor"
    run: /cursor:project.open
    with:
      root: "D:/AI-Agent"

  - name: "Create + open file"
    run: /cursor:files.create+open
    with:
      filepath: "D:/AI-Agent/notes/TODO.md"
      text: "# TODO\n- [ ] Hook Agent → Cursor\n"

  - name: "Insert scaffold"
    run: /cursor:editor.insert
    with:
      filepath: "D:/AI-Agent/notes/TODO.md"
      position: "end"
      text: "\n- [ ] Add UI tasks\n"

  - name: "Save file"
    run: /cursor:editor.save
    with:
      filepath: "D:/AI-Agent/notes/TODO.md"

  - name: "Run terminal in repo"
    run: /cursor:terminal.run
    with:
      cwd: "D:/AI-Agent"
      command: "git status"
```

Реализация `/cursor:...` алиасов зависит от вашей команды исполнения шагов. Проще всего — в обработчике шагов делать POST на `http://127.0.0.1:8088/cursor/<action>`.

---

## 6) Быстрый тест прокси: scripts/cursor_proxy_tests.ps1

```powershell
# scripts\cursor_proxy_tests.ps1
$api = "http://127.0.0.1:8088"
$sec = $env:AGENT_API_SECRET

# Открыть файл
Invoke-WebRequest -Uri "$api/cursor/open" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ filepath="D:\\AI-Agent\\README.md" } | ConvertTo-Json) | Select -Expand Content

# Вставить текст
Invoke-WebRequest -Uri "$api/cursor/insert" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ filepath="D:\\AI-Agent\\README.md"; position="end"; text="`nHello from Agent → Cursor!" } | ConvertTo-Json) | Select -Expand Content

# Терминал
Invoke-WebRequest -Uri "$api/cursor/terminal" -Headers @{ 'x-agent-secret'=$sec } -Method POST -ContentType 'application/json' -Body (@{ cwd="D:\\AI-Agent"; command="dir" } | ConvertTo-Json) | Select -Expand Content
```

---

## 7) Трюки и адаптация

- Если у Cursor API WebSocket/stream для терминала/чатов — добавьте в CursorClient отдельные методы (через websocket-client или websockets) и расширьте карту полей.

- Если требуются workspaceId/tabId — внесите их в payload_templates и прокидывайте из with: в шагах.

- Если аутентификация cookie — укажите auth.type = "cookie" и сделайте заголовок Cookie: name=value в _headers() (или используйте requests.Session() с установкой cookie).

- Если API имеет rate limit — добавьте простую ретри-логику/экспоненциальную паузу вокруг requests.request(...).

---

## 8) Чек-лист запуска (коротко)

1. Задайте `CURSOR_API_URL` и `CURSOR_API_KEY` в сессии.

2. Заполните реальные пути/поля в `cursor_api_map.json`.

3. Добавьте `cursor_client.py` и прокси-роуты `/cursor/*` в агент.

4. Перезапустите FastAPI.

5. Запустите `scripts/cursor_proxy_tests.ps1` — проверьте, что файл открылся/вставился текст/выполнилась команда.

6. Добавьте шаги `/cursor:*` в ProjectSpec.yml и прогоните через ваш `/run-spec`.

---

## 9) Безопасность

- Прокси `/cursor/*` защищены тем же `x-agent-secret`.

- API ключ Cursor не логируем; не коммитим `cursor_api_map.json` с секретами.

- При необходимости разрешайте только белый список команд (например, только open/insert/save/terminal.run с конкретными каталогами).

---

**Готово. Теперь АГЕНТ даёт команды Cursor. Подставьте конкретные пути/поля вашего Cursor API, и мост начнёт работать без правок остальной системы.**
