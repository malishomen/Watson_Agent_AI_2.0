# AI-Agent × Cursor — как запускать и управлять

## Быстрый старт
1) Запусти API агента:
   ```powershell
   cd D:\AI-Agent
   $env:AGENT_HTTP_SHARED_SECRET = "REPLACE_WITH_YOUR_SECRET"
   uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info
   ```

2. Проверка:

   ```powershell
   irm http://127.0.0.1:8088/health
   ```

## Переменные окружения (Cursor → .vscode/settings.json)

* `AGENT_API_BASE`             → [http://127.0.0.1:8088](http://127.0.0.1:8088)
* `AGENT_HTTP_SHARED_SECRET`   → ваш секрет (тот же, что в API)

## Основные эндпоинты

* `GET /health` — проверка
* `POST /command` — универсальные команды (RU/EN или /slash)

  ```json
  { "text": "запусти notepad", "session": "Cursor" }
  ```
* `POST /project/validate` — проверка ProjectSpec.yml

  ```json
  { "spec_path": "D:/AI-Agent/Projects/demo/ProjectSpec.yml" }
  ```
* `POST /project/run` — запуск проекта

  ```json
  { "project_id": "demo", "resume": true }
  ```
* `GET /project/status?project_id=demo` — статус проекта
* `GET /approvals/pending` — список заявок на подтверждение
* `/approve AP-XXXX` — подтверждение в чате (через /command)

## Примеры текстовых команд

* `где я` → /pwd
* `запусти notepad` → /run "notepad"
* `прочитай D:\AI-Agent\README.md` → /read …
* `запиши в D:\AI-Agent\file.txt: Привет` → /write …
* `запусти проект demo` → /project.run demo
* `статус проекта demo` → /project.status demo

## Безопасность

* Заголовок `x-agent-secret` обязателен.
* Белые списки: D:\AI-Agent, D:\Projects, D:\Temp.
* Вне белых зон действия идут через approvals.

