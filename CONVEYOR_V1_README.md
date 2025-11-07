# Watson Agent Conveyor v1 — Инструкция по запуску

## 🎯 Что реализовано

Полностью автономная система разработки с поддержкой:

1. **UTF-8 окружение** - безопасная работа с кириллицей в терминале
2. **Task Watcher** - автоматический подхват задач из `inbox/`
3. **Cursor Tasks** - хоткеи для быстрого запуска
4. **Telegram Bridge** - одиночный экземпляр с PID-lock
5. **Единый роутер** - `/relay/submit` для универсальной обработки
6. **Безопасный repo_path** - привязка проектов к чатам

## 📋 Компоненты

### Файлы

```
Watson_Agent_2.0/
├── scripts/
│   ├── Env-UTF8.ps1           # UTF-8 окружение
│   ├── task_watcher.py        # Автопулл из inbox/
│   ├── make_task.ps1          # Создание задач
│   ├── telegram_bridge.py     # Telegram мост (обновлён)
│   └── Start-WatsonApi.ps1    # Запуск API
├── utils/
│   └── router_core.py         # Единый роутер задач
├── api/
│   └── fastapi_agent.py       # API с /relay/submit
├── .cursor/
│   └── tasks.code.json        # Cursor хоткеи
└── tests/
    ├── test_router_core.py    # ✅ Тесты роутера
    └── test_relay_api.py      # ⚠️ Требует совместимый starlette
```

## 🚀 Быстрый старт

### 1. Подготовка окружения (один раз)

В Cursor откройте **Command Palette** (Ctrl+Shift+P) → **Tasks: Run Task** → выберите:

```
0) Prepare UTF-8 Env
```

Это установит переменные окружения:
- `PYTHONUTF8=1`
- `PYTHONIOENCODING=UTF-8`
- `WATSON_API_BASE=http://127.0.0.1:8090`
- `OPENAI_BASE_URL=http://127.0.0.1:1234/v1`
- `WATSON_PLANNER_MODEL=deepseek-r1-distill-qwen-14b-abliterated-v2`
- `WATSON_CODER_MODEL=qwen2.5-coder-7b-instruct`

### 2. Запуск системы (по порядку)

```
1) Start API (smart)                    # Запуск FastAPI на :8090
2) Start Telegram Bridge (single)       # Telegram мост (одиночный)
3) Start Task Watcher                   # Watcher для inbox/
```

### 3. Проверка здоровья

```
Health: API /health
```

Должен вернуть: `{"ok": true}`

## 💡 Использование

### Вариант A: Через хоткей (быстро)

1. **Выделите** текст задачи в редакторе, например:

```
создай проект people_counter
FastAPI + React
endpoints: /count, /reset
кнопки +/–, reset
unit + e2e smoke
```

2. **Запустите task:**
   - **Relay: Apply+Test (from selection)** — выполнить сразу
   - **Relay: Dry-Run (from selection)** — только посмотреть diff

### Вариант B: Через inbox (автоматически)

1. **Выделите** задачу
2. **Запустите:**
   - **Inbox: Create Task from selection (Apply)**
   - **Inbox: Create Task from selection (Dry-Run)**

3. Файл появится в `inbox/*.task.json`, watcher автоматически отправит в API

### Вариант C: Через Telegram

Если настроен `TELEGRAM_TOKEN`:

```
/run создай проект todo_app
/dryrun добавь типы в api/agent.py
/where    — текущий проект
/list     — все проекты
/use <name> — переключить проект
```

## 🔧 Архитектура

```
Пользователь (Cursor/Telegram/inbox)
    ↓
/relay/submit (роутер)
    ↓
┌─────────────────────┐
│ plan_and_route()    │ → DeepSeek-R1 (опционально)
│ Определяет intent   │
└─────────────────────┘
    ↓
┌─────────────┬──────────────┬─────────────┐
│ help/ping   │ project_create│    code     │
└─────────────┴──────────────┴─────────────┘
                    ↓                ↓
            PROJECT_TEMPLATE.ps1   /autocode/generate
                                      ↓
                                 Qwen2.5-Coder
                                      ↓
                              Патч + Тесты
```

## 📝 Примеры задач

### Создание проекта

```
создай проект weather_app
```

→ Создаст структуру в `D:\projects\Projects_by_Watson_Local_Agent\weather_app\`

### Кодовая задача

```
/run Add comprehensive logging to utils/safe_call.py
- Use structlog
- Log entry, exit, exceptions
- Include timestamps and context
```

→ Сгенерирует diff, применит, запустит тесты

### Dry-run (только просмотр)

```
/dryrun Refactor api/fastapi_agent.py
Extract all /cursor/* endpoints to separate router
```

→ Покажет diff без применения

## 🧪 Тесты

### Запуск всех тестов

```powershell
py -3.11 -m pytest -v
```

### Только роутер

```powershell
py -3.11 -m pytest tests/test_router_core.py -v
```

Результат:
```
✅ test_slugify_basic PASSED
✅ test_slugify_cyrillic PASSED
✅ test_plan_and_route_help PASSED
✅ test_plan_and_route_ping PASSED
✅ test_plan_and_route_project_create PASSED
✅ test_plan_and_route_code_fallback PASSED
```

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `WATSON_API_BASE` | `http://127.0.0.1:8090` | Адрес Watson API |
| `OPENAI_BASE_URL` | `http://127.0.0.1:1234/v1` | LM Studio endpoint |
| `OPENAI_API_KEY` | `lm-studio` | API ключ (dummy) |
| `WATSON_PLANNER_MODEL` | `deepseek-r1-distill-qwen-14b-abliterated-v2` | Модель для планирования |
| `WATSON_CODER_MODEL` | `qwen2.5-coder-7b-instruct` | Модель для кода |
| `TELEGRAM_TOKEN` | - | Токен бота (опционально) |
| `TELEGRAM_CHAT_ID` | - | ID чата для фильтрации |

### config.toml

```toml
repo_path = "D:\\projects\\Ai-Agent_Watson\\Watson_Agent_2.0"
test_cmd = "py -3.11 -m pytest -q"

[models]
reasoning_model = "deepseek-r1-distill-qwen-14b-abliterated-v2"
coder_model = "qwen2.5-coder-7b-instruct"
diff_generator = "qwen2.5-coder-7b-instruct"
```

## 🐛 Troubleshooting

### Кириллица в терминале не отображается

1. Запустите `0) Prepare UTF-8 Env`
2. Перезапустите терминал в Cursor

### Telegram Bridge запускается дважды

```powershell
# Убить все Python процессы
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Удалить lock
Remove-Item data\telegram_bridge.lock -ErrorAction SilentlyContinue

# Перезапустить
py -3.11 -X utf8 scripts\telegram_bridge.py
```

Или используйте task: **Kill Python + Restart Bridge**

### API не отвечает

```powershell
# Проверка
iwr http://127.0.0.1:8090/health | % Content

# Логи
Get-Content uvicorn.out -Tail 50
Get-Content uvicorn.err -Tail 50
```

### Тесты падают

```powershell
# Переустановка зависимостей
py -3.11 -m pip install --upgrade fastapi pydantic pytest

# Запуск с verbose
py -3.11 -m pytest -vvs
```

## 📦 Зависимости

```txt
fastapi>=0.104.0
pydantic>=2.0.0
uvicorn>=0.24.0
pytest>=7.4.0
requests>=2.31.0
```

## 🎉 Definition of Done

✅ Терминал показывает кириллицу  
✅ Telegram Bridge — одиночный экземпляр  
✅ Задачи отправляются одним хоткеем  
✅ Кодовые задачи идут в активный проект чата  
✅ `/relay/submit` маршрутизирует корректно  
✅ Тесты `test_router_core.py` проходят  

## 🔜 Следующие шаги (Conveyor v2)

1. Шаблон фронтенда (Vite/React)
2. E2E тесты (Playwright)
3. Dockerfile + compose.yaml
4. Провижининг (Ansible/Terraform)
5. Автодеплой

---

**Версия:** Conveyor v1  
**Дата:** 2025-10-08  
**Статус:** ✅ Production Ready



