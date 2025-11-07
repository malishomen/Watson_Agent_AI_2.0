# 🔄 Конвейер → Cursor: Руководство по настройке

## 🎯 Проблема

**"Конвейер не передает задачи в Cursor"**

Когда задача приходит через `/relay/submit` (из Telegram или другого источника), она обрабатывается API, но **не попадает в Cursor для выполнения**.

---

## 🔍 Причина

**Cursor IDE НЕ предоставляет HTTP API для получения задач извне.**

Это означает, что Watson Agent не может напрямую "позвать" Cursor и сказать "выполни эту задачу".

---

## ✅ РЕШЕНИЕ: File-Based System

Создана система передачи задач через файлы:

```
Telegram → /relay/submit → inbox/*.task.json → Cursor Task Sender → cursor_tasks/*.md → Cursor AI
```

### Как это работает:

1. **Пользователь** отправляет задачу в Telegram
2. **Telegram Bridge** отправляет в `/relay/submit`
3. **API** создает файл `inbox/task_1234.task.json`
4. **Cursor Task Sender** читает задачу и создает `cursor_tasks/task_1234_instruction.md`
5. **Вы** открываете файл в Cursor и отправляете в Chat (Ctrl+L)
6. **Cursor AI** выполняет задачу автоматически!

---

## 🚀 Быстрый старт

### Вариант 1: Автоматический (рекомендуется)

```powershell
cd D:\projects\Ai-Agent_Watson\Watson_Agent_2.0
.\START_FULL_SYSTEM.ps1
```

Запустит:
- ✅ Watson API (port 8090)
- ✅ Telegram Bridge (long-polling)
- ✅ Task Watcher (inbox monitoring)

### Вариант 2: Ручной запуск

```powershell
# 1. Включить делегацию в Cursor
[Environment]::SetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','true','User')

# 2. Запустить Watson API
.\scripts\Start-WatsonApi.ps1 -Port 8090

# 3. Запустить Telegram Bridge (в новом окне)
py -3.11 -X utf8 scripts\telegram_bridge.py

# 4. Запустить Cursor Task Sender (в новом окне)
py -3.11 scripts\cursor_task_sender.py
```

---

## 📋 Как использовать

### Шаг 1: Отправить задачу

**Через Telegram:**
```
Добавь логирование в функцию calculate_total
```

**Через API:**
```powershell
$body = @{
    text = "Add type hints to authentication module"
    dry_run = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8090/relay/submit `
  -Method POST -ContentType "application/json" -Body $body
```

**Через inbox (вручную):**
```powershell
.\scripts\make_task.ps1 -Text "Refactor user service"
```

### Шаг 2: Дождаться инструкции

Cursor Task Sender создаст файл:
```
cursor_tasks/task_1234_instruction.md
```

В консоли увидите:
```
📥 Processing: task_1234.task.json
✅ Создана инструкция: task_1234_instruction.md
   📄 Откройте файл в Cursor и отправьте в Chat!
   📂 Путь: D:\...\cursor_tasks\task_1234_instruction.md
```

### Шаг 3: Выполнить в Cursor

1. **Откройте файл** `cursor_tasks/task_1234_instruction.md` в Cursor
2. **Выделите весь текст** (Ctrl+A)
3. **Откройте Cursor Chat** (Ctrl+L)
4. **Вставьте текст** и нажмите Enter
5. **Cursor AI начнет выполнение** автоматически!

### Шаг 4: Проверить результат

Cursor создаст файл:
```
cursor_tasks/task_1234_result.md
```

С отчетом о выполненной работе.

---

## 🔧 Компоненты системы

### 1. **Watson API** (`api/fastapi_agent.py`)

Endpoint `/relay/submit`:
- Принимает задачу
- Определяет intent
- Если `WATSON_USE_CURSOR_DELEGATION=true` → создает файл в `inbox/`
- Иначе → выполняет через `/autocode/generate` напрямую

### 2. **Cursor Task Sender** (`scripts/cursor_task_sender.py`)

- Мониторит папку `inbox/`
- Читает `*.task.json` файлы
- Создает детальные инструкции в `cursor_tasks/*.md`
- Удаляет обработанные задачи из inbox

### 3. **Cursor AI** (ваше участие)

- Открывает файлы из `cursor_tasks/`
- Получает инструкции
- Выполняет задачу
- Создает отчет

---

## 📊 Текущий статус

```
✅ Watson API: Running (port 8090)
✅ Telegram Bridge: Running (PID: 22580)
✅ Task Watcher: Running (PID: 26456)
✅ WATSON_USE_CURSOR_DELEGATION: enabled
❌ Cursor Task Sender: НЕ ЗАПУЩЕН
```

---

## 🚀 Запуск Cursor Task Sender

### Вариант 1: В отдельном окне

```powershell
cd D:\projects\Ai-Agent_Watson\Watson_Agent_2.0
py -3.11 scripts\cursor_task_sender.py
```

Увидите:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📋 CURSOR TASK SENDER - ЗАПУЩЕН
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👀 Watching: D:\...\inbox
📤 Output:   D:\...\cursor_tasks
```

### Вариант 2: Как фоновый процесс

```powershell
Start-Process -FilePath "py" -ArgumentList "-3.11","scripts\cursor_task_sender.py" -WindowStyle Hidden
```

---

## 🧪 Тестирование

### Тест 1: Создать задачу вручную

```powershell
.\scripts\make_task.ps1 -Text "Add comment to main function"
```

**Ожидается:**
1. Создан `inbox/task_XXXX.task.json`
2. Cursor Task Sender обработает его
3. Появится `cursor_tasks/task_XXXX_instruction.md`
4. В консоли покажется путь к файлу

### Тест 2: Через Telegram

Отправьте боту:
```
Добавь type hints в модуль utils
```

**Ожидается:**
1. Telegram Bridge → `/relay/submit`
2. API создает `inbox/task_XXXX.task.json`
3. Cursor Task Sender создает инструкцию
4. Вы открываете и отправляете в Cursor Chat

### Тест 3: Через API

```powershell
$body = @{
    text = "Refactor authentication to use async/await"
    dry_run = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8090/relay/submit `
  -Method POST -ContentType "application/json" -Body $body
```

---

## 📁 Структура папок

```
Watson_Agent_2.0/
├── inbox/                    # Входящие задачи (JSON)
│   └── task_1234.task.json  ← создается API
├── cursor_tasks/             # Инструкции для Cursor (Markdown)
│   ├── task_1234_instruction.md  ← создается Cursor Task Sender
│   └── task_1234_result.md       ← создается Cursor AI
└── data/
    └── processed_tasks.log   # Лог обработанных задач
```

---

## 🔄 Полный workflow

```mermaid
graph LR
    A[Telegram] -->|текст| B[/relay/submit]
    B -->|создает| C[inbox/task.json]
    C -->|мониторинг| D[Cursor Task Sender]
    D -->|создает| E[cursor_tasks/instruction.md]
    E -->|открыть| F[Cursor AI]
    F -->|выполняет| G[изменения в коде]
    F -->|создает| H[cursor_tasks/result.md]
```

---

## 🎛️ Настройки

### Включить/выключить делегацию в Cursor

```powershell
# Включить (задачи идут в inbox для Cursor)
[Environment]::SetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','true','User')

# Выключить (задачи выполняются API напрямую через LLM)
[Environment]::SetEnvironmentVariable('WATSON_USE_CURSOR_DELEGATION','false','User')
```

### Проверить статус

```powershell
$env:WATSON_USE_CURSOR_DELEGATION
```

---

## 🛠️ Troubleshooting

### Задачи не попадают в inbox

**Проверьте:**
```powershell
# Включена ли делегация?
$env:WATSON_USE_CURSOR_DELEGATION  # должно быть 'true'

# Перезапустите API
Get-Process python | Stop-Process -Force
.\scripts\Start-WatsonApi.ps1 -Port 8090
```

### Cursor Task Sender не видит задачи

**Проверьте:**
```powershell
# Запущен ли процесс?
Get-Process python | Where-Object { 
    (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*cursor_task_sender*"
}

# Есть ли файлы в inbox?
Get-ChildItem inbox\*.task.json
```

### Cursor не выполняет задачу

**Убедитесь что:**
1. Открыли файл `cursor_tasks/task_XXXX_instruction.md`
2. Выделили ВСЬ текст (Ctrl+A)
3. Вставили в Cursor Chat (Ctrl+L, Ctrl+V, Enter)
4. Cursor получил инструкции

---

## 💡 Альтернативные подходы

### Подход 1: File-Based (текущий) ⭐
- ✅ Работает сейчас
- ✅ Не требует изменений Cursor
- ⚠️ Требует ручное открытие файлов

### Подход 2: UI Automation
```python
from api.cursor_automation_agent import CursorAutomationAgent
agent = CursorAutomationAgent()
agent.send_task_to_cursor("Add logging")
```
- ✅ Полностью автоматически
- ⚠️ Требует активное окно Cursor

### Подход 3: Cursor Extension (будущее)
Создать extension который слушает HTTP/WebSocket
- 🔮 Лучшее решение
- ⚠️ Требует разработку extension

---

## 📊 Сравнение режимов

| Режим | Делегация | Как работает |
|-------|-----------|--------------|
| **WATSON_USE_CURSOR_DELEGATION=false** | ❌ | API выполняет через LLM сам |
| **WATSON_USE_CURSOR_DELEGATION=true** | ✅ | API создает задачу для Cursor |

---

## 🎯 Рекомендации

### Используйте делегацию когда:
- ✅ Задача сложная и требует Cursor AI
- ✅ Нужен контроль над выполнением
- ✅ Хотите review перед применением

### Используйте прямое выполнение когда:
- ✅ Задача простая
- ✅ Нужна автоматизация без участия
- ✅ Доверяете LLM модели

---

## 📝 Пример полного цикла

```powershell
# 1. Запуск системы
.\START_FULL_SYSTEM.ps1

# 2. Запуск Cursor Task Sender (в новом окне PowerShell)
py -3.11 scripts\cursor_task_sender.py

# 3. Создание задачи
.\scripts\make_task.ps1 -Text "Add logging to user module"

# 4. Наблюдение
# В консоли Cursor Task Sender увидите:
# 📥 Processing: task_1234.task.json
# ✅ Создана инструкция: task_1234_instruction.md

# 5. Выполнение в Cursor
# - Откройте cursor_tasks/task_1234_instruction.md
# - Ctrl+A → Ctrl+L → Ctrl+V → Enter
# - Cursor выполнит задачу!

# 6. Проверка результата
# - Смотрите cursor_tasks/task_1234_result.md
# - Проверяйте изменения в коде
```

---

## 🎉 Итого

**✅ Создана полная система передачи задач в Cursor!**

**Компоненты:**
1. ✅ `START_FULL_SYSTEM.ps1` - запуск всех сервисов
2. ✅ `scripts/make_task.ps1` - создание задач вручную
3. ✅ `scripts/cursor_task_sender.py` - мониторинг и создание инструкций
4. ✅ `api/fastapi_agent.py` - поддержка WATSON_USE_CURSOR_DELEGATION
5. ✅ Система `inbox/` → `cursor_tasks/`

**Что делать:**
1. Запустите `.\START_FULL_SYSTEM.ps1`
2. В новом окне запустите `py -3.11 scripts\cursor_task_sender.py`
3. Отправьте задачу боту или создайте вручную
4. Откройте инструкцию из `cursor_tasks/` в Cursor
5. Отправьте в Cursor Chat
6. Наслаждайтесь автоматикой! 🎯

---

**"Делегируй правильно - получай результат!"** 🚀

