# 📱 Watson Agent 2.0 - Telegram Integration

## Концепция

Вы пишете задачи в Telegram → Бот пересылает их в локальный API → Агент генерирует diff, применяет, тестирует → Результат приходит обратно в Telegram.

**Всё управляется из Cursor через Tasks!**

---

## 🚀 Быстрая настройка (3 шага)

### Шаг 1: Проверка переменных окружения

```powershell
# Должны быть установлены на уровне User
[Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
[Environment]::GetEnvironmentVariable('TELEGRAM_CHAT_ID','User')
```

Если пусто — выполните:

```powershell
# Замените на ваши значения
[Environment]::SetEnvironmentVariable('TELEGRAM_TOKEN', 'ваш_токен_бота', 'User')
[Environment]::SetEnvironmentVariable('TELEGRAM_CHAT_ID', 'ваш_chat_id', 'User')
```

### Шаг 2: Запуск из Cursor

1. Откройте **Cursor**
2. Нажмите `Ctrl+Shift+P` → `Tasks: Run Task`
3. Запустите **Start API (smart)**
4. Запустите **Start Telegram Bridge**

Терминал покажет:
```
🤖 Watson Telegram Bridge starting...
   API: http://127.0.0.1:8090
   Repo: D:\projects\Ai-Agent_Watson\Watson_Agent_2.0
   Chat filter: 123456789
```

### Шаг 3: Отправка задачи через Telegram

В вашем боте напишите:

```
/run Add logging to calculate_total function in utils/math.py
```

Или для dry-run:

```
/dryrun Refactor user_auth to use async/await
```

---

## 📝 Команды бота

### `/run <задача>`

Полный цикл: генерация diff → применение (git + fallback) → pytest → отчёт

**Пример:**
```
/run Add type hints to all functions in api/agent.py
```

**Ответ бота:**
```
✅ APPLIED | 🟢 TESTS PASSED
Diff: 1024 bytes
Repo: Watson_Agent_2.0

Logs:
[validate] ok
[git apply --check]
error: corrupt patch at line 15
[fallback in-memory]
patched api/agent.py (fallback, 156 lines)

15 passed, 6 skipped in 11.2s
```

### `/dryrun <задача>`

Только генерация diff без применения

**Пример:**
```
/dryrun Add docstrings to all public methods
```

**Ответ бота:**
```
🧪 DRY-RUN | 🧩 PATCH FAILED
Diff: 2048 bytes
Repo: Watson_Agent_2.0

Logs:
dry-run

[diff preview:]
--- api/agent.py
+++ api/agent.py
...
```

---

## 🔧 Workflow из Cursor

### Вариант A: Через Telegram (рекомендуется)

1. **Cursor** → `Ctrl+Shift+P` → `Tasks: Run Task` → **Start API (smart)**
2. **Cursor** → `Ctrl+Shift+P` → `Tasks: Run Task` → **Start Telegram Bridge**
3. **Telegram** → пишите задачи боту
4. **Telegram** → получаете результаты
5. **Cursor** → проверяете изменения через `git diff`

### Вариант B: Из Cursor напрямую (без Telegram)

1. Выделите текст задачи в редакторе
2. `Ctrl+Shift+P` → `Tasks: Run Task`
3. Выберите **Send to Agent (Apply+Test)**
4. Результат появится в терминале Cursor

---

## 🎯 Примеры задач

### Простые

```
/run Add blank line after imports in utils/safe_call.py
/dryrun Rename function old_name to new_name in api/agent.py
/run Fix typo in comment on line 42 of tools/patcher.py
```

### Средние

```
/run Refactor calculate_total to use list comprehension
/run Add error handling to http_post function
/dryrun Extract magic numbers to constants in config.toml
```

### Сложные

```
/run Implement caching for LLM responses with TTL 300 seconds
/run Add async support to all API endpoints
/dryrun Migrate from subprocess to asyncio.create_subprocess_exec
```

---

## 📊 Типы ответов

### ✅ Успех (git apply)

```
✅ APPLIED | 🟢 TESTS PASSED
Diff: 256 bytes

Logs:
[validate] ok
$ git apply ...
Applied successfully
15 passed in 11.2s
```

### ✅ Успех (fallback)

```
✅ APPLIED | 🟢 TESTS PASSED
Diff: 512 bytes

Logs:
[validate] ok
[git apply --check] error: corrupt patch
...6 git strategies failed...
[fallback in-memory]
patched file.py (fallback, 89 lines)
15 passed in 11.3s
```

### 🧩 Патч не применился

```
🧩 PATCH FAILED | ⚪ NO TESTS
Diff: 128 bytes

Logs:
[validate] inconsistent filenames
All strategies failed
[fallback in-memory]
fallback error: target not found
```

### 🔴 Тесты упали

```
✅ APPLIED | 🔴 TESTS FAILED
Diff: 384 bytes

Logs:
[fallback in-memory]
patched api/agent.py (fallback, 156 lines)

FAILED tests/test_agent.py::test_respond
AssertionError: ...
1 failed, 14 passed in 11.5s
```

---

## 🛠️ Troubleshooting

### Бот не отвечает

```powershell
# 1. Проверьте, запущен ли bridge
Get-Process -Name python | Where-Object { $_.CommandLine -match "telegram_bridge" }

# 2. Проверьте токен
$token = [Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
Invoke-WebRequest "https://api.telegram.org/bot$token/getMe"

# 3. Перезапустите bridge в Cursor
# Tasks → Start Telegram Bridge
```

### API недоступен

```powershell
# Проверьте статус
Invoke-WebRequest http://127.0.0.1:8090/health

# Если упало — перезапустите
# Cursor → Tasks → Start API (smart)
```

### Патч применился, но тесты не запустились

Проверьте `config.toml`:

```toml
test_cmd = 'py -3.11 -m pytest -q -k "not integration"'
```

Кавычки должны быть одинарными снаружи, двойными внутри!

---

## 🎮 Горячие клавиши в Cursor (рекомендуется)

Добавьте в `keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+t",
    "command": "workbench.action.tasks.runTask",
    "args": "Run Tests"
  },
  {
    "key": "ctrl+shift+a",
    "command": "workbench.action.tasks.runTask",
    "args": "Start API (smart)"
  },
  {
    "key": "ctrl+shift+b",
    "command": "workbench.action.tasks.runTask",
    "args": "Start Telegram Bridge"
  }
]
```

Теперь:
- `Ctrl+Shift+A` → запуск API
- `Ctrl+Shift+B` → запуск Telegram моста
- `Ctrl+Shift+T` → быстрые тесты

---

## 💡 Продвинутые сценарии

### Мониторинг в реальном времени

Откройте 2 терминала в Cursor:

**Терминал 1:**
```powershell
Get-Content .\uvicorn_8090.out.log -Wait -Tail 20
```

**Терминал 2:**
```powershell
py -3.11 scripts\telegram_bridge.py
```

Теперь видите live-логи API и моста одновременно.

### Переключение на DeepSeek для сложных diff

```powershell
# В PowerShell терминале Cursor
$env:WATSON_DIFF_MODEL = "deepseek-r1-distill-qwen-14b-abliterated-v2"

# Перезапустите API
# Cursor → Tasks → Start API (smart)
```

### Batch обработка задач

Создайте файл `tasks.txt`:
```
Add logging to function A
Add error handling to function B
Refactor function C to use async
```

Запустите:
```powershell
Get-Content tasks.txt | ForEach-Object {
    $body = @{task=$_; repo_path=(Get-Location).Path; dry_run=$false} | ConvertTo-Json
    iwr http://127.0.0.1:8090/autocode/generate -Method POST -ContentType 'application/json' -Body $body
    Start-Sleep -Seconds 5
}
```

---

## 🔐 Безопасность

- Токены хранятся в User env (не в коде/git)
- Bridge фильтрует по `CHAT_ID` (только ваш чат)
- API работает только на localhost (127.0.0.1)
- Логи маскируют sensitive data
- `.gitignore` исключает `.env`, токены, логи

---

## 📈 Статистика и метрики

Bridge логирует каждую команду:

```
📨 [123456789]: /run Add logging to calculate_total
```

API логирует в `uvicorn_8090.out.log`:

```
INFO: 127.0.0.1:xxxxx - "POST /autocode/generate HTTP/1.1" 200 OK
```

Telegram отправляет детальный отчёт:
- Размер diff
- Статус применения (git/fallback)
- Результат тестов
- Хвост логов (1200 символов)

---

## ✨ Готовая система!

**Из Cursor:**
1. `Ctrl+Shift+P` → `Tasks: Run Task` → **Start API (smart)**
2. `Ctrl+Shift+P` → `Tasks: Run Task` → **Start Telegram Bridge**

**Из Telegram:**
3. Пишите задачи боту
4. Получайте результаты

**Проверка в Cursor:**
5. `git diff` — смотрите изменения
6. `git commit -am "описание"` — коммитите

Автономная разработка готова! 🚀

