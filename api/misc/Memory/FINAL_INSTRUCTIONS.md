# ⚡ Быстрый старт (3 шага)

1. Открой проект в Cursor: `D:\AI-Agent`
2. Проверь секрет и переменные в `.vscode\settings.json` (см. «Переменные» ниже).
3. `Ctrl+Shift+P` → **Tasks: Run Task** → **AA: Start API**
   Ожидаем в терминале: `Uvicorn running on http://127.0.0.1:8088` → без ошибок.

Проверка:

```powershell
Ctrl+Shift+P → Tasks: Run Task → AA: Health Check
# ожидаем: {"status":"ok"}
```

---

# 🎛 Горячие клавиши и задачи Cursor

`Ctrl+Shift+P` → **Tasks: Run Task** и выбирай:

1. **AA: Start API** — запускает FastAPI агента с корректными флагами (UTF-8, h11, 1 worker).
2. **AA: Health Check** — проверка `/health`.
3. **AA: Command (prompt)** — спросит текст; отправит в `/command`.
4. **AA: Approvals Pending** — покажет все ожидающие подтверждения.
5. **AA: Project Validate (prompt path)** — валидация `ProjectSpec.yml`.
6. **AA: Project Run (prompt id)** — запуск проекта по ID.
7. **AA: Project Status (prompt id)** — статус проекта.
8. **🔥 AA: Scaffold FastAPI+Postgres** — **собирает проект FastAPI + Postgres + Docker Compose с нуля** (новая кнопка).

> Все эти задачи уже добавлены/обновлены в `.vscode/tasks.json`.
> Скрипты лежат в `scripts\…`, включая **`scripts\scaffold_fastapi_project.ps1`**.

---

# ✅ Контрольные проверки (скопируй по очереди)

## 1) Базовые эндпоинты

```powershell
# Health (из Tasks уже проверили, но можно вручную):
irm http://127.0.0.1:8088/health

# Pending approvals:
$h=@{"x-agent-secret"=$env:AI_AGENT_HTTP_SECRET}
irm http://127.0.0.1:8088/approvals/pending -Headers $h
```

Ожидаем: `{"status":"ok"}` и `[]` либо список заявок.

## 2) Универсальный /command (нативный язык → действие)

```powershell
$h=@{"x-agent-secret"=$env:AI_AGENT_HTTP_SECRET}

# где я
$body=@{ text="где я"; session="TG" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# запусти notepad
$body=@{ text="запусти notepad"; session="TG" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# прочитай файл
$body=@{ text="прочитай D:\AI-Agent\README.md"; session="TG" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

Ожидаем: корректные ответы без `<think>`.

## 3) LLM через роутер (LM Studio → OpenAI fallback)

```powershell
$h=@{"x-agent-secret"=$env:AI_AGENT_HTTP_SECRET}
$body=@{ text="ответь одним словом: pong"; session="TG" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

Ожидаем: `pong`.
Если пусто — выставь `LMSTUDIO_MODEL`, либо подключи `OPENAI_API_KEY/OPENAI_MODEL` и повтори.

## 4) Project Runner (demo)

```powershell
# Валидация
$body=@{ spec_path="D:/AI-Agent/Projects/demo/ProjectSpec.yml" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/validate -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# Запуск
$body=@{ project_id="demo"; resume=$true } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/run -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# Статус
irm "http://127.0.0.1:8088/project/status?project_id=demo" -Headers $h
```

Ожидаем: `state=done`, шаги выполнены.

---

# 🔥 Кнопка "AA: Scaffold FastAPI+Postgres"

**Что делает:** запускает `scripts\scaffold_fastapi_project.ps1`, создаёт каркас в `D:\Projects\fastapi-starter` (по умолчанию):

* `app/` FastAPI (+ `/items`, `/users`, `/health`)
* `db/` Postgres (Docker volume), `docker-compose.yml`
* `tests/` pytest скелет
* `.env`, `requirements.txt`, `README.md`
* `ProjectSpec.yml` для автоматического прогона через нашего агента

**Как запустить:**

```
Ctrl+Shift+P → Tasks: Run Task → AA: Scaffold FastAPI+Postgres
```

Ожидаем: папки/файлы созданы без ошибок.
Дальше (опционально) можно сразу отдать агенту `ProjectSpec.yml` на прогон:

```powershell
$body=@{ spec_path="D:/Projects/fastapi-starter/ProjectSpec.yml" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/validate -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
$body=@{ project_id="fastapi-starter"; resume=$true } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/run -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

---

# 🧰 Переменные окружения (минимум)

Открой `.vscode/settings.json` и заполни:

```json
{
  "AI_AGENT_HTTP_SECRET": "SUPER_LONG_SECRET",

  "LMSTUDIO_API_BASE": "http://127.0.0.1:1234/v1",
  "LMSTUDIO_MODEL": "ТОЧНЫЙ_ID_МОДЕЛИ_ИЗ_LM_Studio",
  "DEEPSEEK_LOCAL_MODEL": "",

  "OPENAI_API_BASE": "https://api.openai.com/v1",
  "OPENAI_MODEL": "gpt-4.1-mini",          // или свой
  "OPENAI_API_KEY": "sk-..."                // при необходимости fallback'а

  // опционально для Telegram:
  // "TG_BOT_TOKEN": "123456:ABC..."
}
```

> Для Telegram запускай бот так, чтобы не словить `latin-1`:
> `python -X utf8 telegram_bot.py`
> И убедись, что все HTTP-запросы идут с `json=...`, а не `data=...` (у нас уже так сделано).

---

# 🛡 Быстрый troubleshooting

* **401 Unauthorized** → секрет в `.vscode/settings.json` и заголовке `x-agent-secret` должны совпадать.
* **LM Studio молчит / only thinking** → укажи точный `LMSTUDIO_MODEL`, иначе включи `OPENAI_*` для fallback.
* **Кириллица ломается** → в терминале агента используется UTF-8 и `python -X utf8` (у нас задано).
* **Порт занят** → закрой лишние `python/uvicorn`:

  ```powershell
  Get-Process | ? {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force
  ```
* **Файлы/запись требуют /approve** → смотри `AA: Approvals Pending`, подтверди `/approve <ID>`.

---

# 🧪 Что прислать мне после запуска

1. `AA: Health Check` → вывод (`{"status":"ok"}`) — ✅/❌
2. `/command` "где я" → ответ — ✅/❌
3. `/command` "ответь одним словом: pong" → `pong` — ✅/❌
4. `demo` проект: `validate/run/status` — итоговый `state` — ✅/❌
5. **Scaffold FastAPI+Postgres** — факт создания папок/файлов — ✅/❌

---

# 🎯 Готовые файлы в пакете

```
Memory/
├── docs/
│   └── cursor.md                    # Полная документация
├── .vscode/
│   ├── settings.json               # Переменные окружения
│   └── tasks.json                  # 8 готовых задач
├── scripts/
│   ├── start_agent.ps1             # Запуск API агента
│   ├── run_cursor_command.ps1      # Выполнение команд
│   └── scaffold_fastapi_project.ps1 # Создание проекта с нуля
├── COMBAT_CHECKLIST.md             # Боевой чек-лист
├── CURSOR_PACKAGE_README.md         # Инструкции по пакету
└── FINAL_INSTRUCTIONS.md            # Этот файл
```

**Готово к бою!** 🚀

