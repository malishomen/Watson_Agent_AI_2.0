# Cursor — полный гайд по локальному ИИ‑агенту (LM Studio + OpenAI fallback)

> **Проект**: локальный агент с памятью (SQLite), первичный движок — LM Studio, авто‑fallback → OpenAI.  
> **Ключевой скрипт**: `D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py`  
> **База памяти (по умолчанию)**: `D:\AI-Agent\Memory\agent_memory.sqlite`

---

## 0) Предпосылки
- Windows 10/11, права пользователя.
- Установлены: **Python 3.11+**, **PowerShell**, **LM Studio**, (опц.) **Docker**.
- OpenAI ключ для fallback в переменной окружения `OPENAI_API_KEY`.

```powershell
# разово в текущей сессии
$env:OPENAI_API_KEY = "sk-..."
# навсегда для пользователя (новые окна PowerShell)
setx OPENAI_API_KEY "sk-..."
```

---

## 1) Структура проекта (рекомендуемая для Cursor)
```
D:\AI-Agent\
│  README.md
│  .env.example                 # опционально
│
├─Memory\
│  ├─ GPT+Deepseek_Agent_memory.py
│  └─ agent_memory.sqlite       # создаётся автоматически
│
├─venv\                         # виртуальное окружение Python
│  └─ ...
└─cursor\                       # сервисные файлы для Cursor
   ├─ tasks.code.json           # готовые Code Actions / Tasks
   ├─ rules.md                  # системные правила подсказок
   └─ snippets.md               # сниппеты команд/шаблонов
```

> **Минимум для старта**: папка `Memory` и файл `GPT+Deepseek_Agent_memory.py`.

---

## 2) Быстрый старт (PowerShell)
```powershell
# создать venv
python -m venv D:\AI-Agent\venv
# разрешить запуск скриптов активации
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
# активировать venv
D:\AI-Agent\venv\Scripts\Activate.ps1

# переменные окружения (локальный LM Studio)
setx LM_STUDIO_URL "http://127.0.0.1:1234"
setx LM_STUDIO_MODEL "deepseek-r1-distill-qwen-14b-abliterated-v2"
setx AGENT_DB "D:\AI-Agent\Memory\agent_memory.sqlite"

# в текущем окне
$env:LM_STUDIO_URL = "http://127.0.0.1:1234"
$env:LM_STUDIO_MODEL = "deepseek-r1-distill-qwen-14b-abliterated-v2"
$env:AGENT_DB = "D:\AI-Agent\Memory\agent_memory.sqlite"

# зависимости
python -m pip install --upgrade pip requests

# одноразовый запрос (инициализирует БД)
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "Привет!"
```

---

## 3) Настройка LM Studio
1. Открой **Settings → Developer/API**.
2. Включи **Enable Local Server (OpenAI‑compatible)**.
3. Адрес по умолчанию: `http://127.0.0.1:1234` (или выбери другой порт, например 1235).
4. Загрузите и **Run** модель `deepseek-r1-distill-qwen-14b-abliterated-v2`.
5. Тест из PowerShell:
```powershell
Invoke-WebRequest -Uri "$($env:LM_STUDIO_URL)/v1/models" -Method GET | Select-Object -Expand Content
```

---

## 4) What to open в Cursor
Открой в Cursor папку **`D:\AI-Agent`**.

### Рекомендации по структуре Workspace:
- **Root**: `README.md`, `.env.example`, папка `Memory/`, папка `cursor/`.
- В `cursor/` держим служебные правила и задачи для Cursor (см. ниже).

---

## 5) Cursor — правила и контекст (rules.md)
Создай файл `D:\AI-Agent\cursor\rules.md` со следующим содержимым:

```md
# Cursor Rules — AI-Agent (LM Studio + OpenAI)
- Всегда отвечай **на русском**, кратко и по делу.
- Приоритет источников: 1) локальный код в репозитории, 2) инструкции в `cursor/`.
- Не изменяй путь файлов проекта без явного указания.
- Учитывай переменные окружения: LM_STUDIO_URL, LM_STUDIO_MODEL, OPENAI_API_KEY, AGENT_DB.
- Если задача требует внешних зависимостей — добавляй их через `pip` и фиксируй команду.
- Не добавляй неиспользуемые зависимости.
- В PR/патчах указывай: **что** меняется, **почему**, **как тестировать**.
- Не оставляй `print`/`debug` в коде в финале.
```

> Подключай `rules.md` к подсказке Cursor (Use file as context) при Code Actions.

---

## 6) Cursor — задачи/экшены (tasks.code.json)
Создай `D:\AI-Agent\cursor\tasks.code.json`:

```json
[
  {
    "title": "Agent: run once",
    "description": "Одноразовый запрос к агенту",
    "prompt": "Выполни одноразовый запуск агента со строкой запроса ниже и покажи stdout.",
    "steps": [
      {
        "type": "terminal",
        "command": "python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session Danil-PC --once \"$INPUT\""
      }
    ]
  },
  {
    "title": "Agent: start chat",
    "description": "Запуск интерактивного чата",
    "steps": [
      {
        "type": "terminal",
        "command": "python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session Danil-PC"
      }
    ]
  },
  {
    "title": "DB: wipe memory",
    "description": "Удалить файл памяти (SQLite)",
    "confirm": true,
    "steps": [
      {
        "type": "terminal",
        "command": "powershell Remove-Item D:/AI-Agent/Memory/agent_memory.sqlite -Force"
      }
    ]
  },
  {
    "title": "LM Studio: ping models",
    "description": "Проверка, что локальный сервер отвечает",
    "steps": [
      {
        "type": "terminal",
        "command": "powershell Invoke-WebRequest -Uri \"$env:LM_STUDIO_URL/v1/models\" -Method GET | Select-Object -Expand Content"
      }
    ]
  }
]
```

> В Cursor: **Run Task → выбери нужную** → введи `$INPUT` при необходимости.

---

## 7) Cursor — сниппеты (snippets.md)
`D:\AI-Agent\cursor\snippets.md` — быстрые вставки:

```md
### /remember — сохранить заметку
python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/remember Моя новая заметка"

### /recall — показать последнюю заметку
python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/recall"

### /notes — 10 последних
python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/notes"

### Проверка fallback к OpenAI
$env:LM_STUDIO_URL = "http://127.0.0.1:9999"
python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "Проверка fallback"
```

---

## 8) Чек‑лист разработчика в Cursor
- [ ] LM Studio запущен и слушает порт (по умолчанию 1234).
- [ ] Установлен venv, активирован `D:\AI-Agent\venv`.
- [ ] В `.env`/переменных: `OPENAI_API_KEY`, `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `AGENT_DB`.
- [ ] Скрипт агента доступен по пути `D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py`.
- [ ] Выполнен «run once» и создана БД `agent_memory.sqlite`.
- [ ] Тестированы /remember, /recall, /notes.
- [ ] Проверен fallback.

---

## 9) Типовые задачи для Cursor (шаблон подсказки)
```md
**Задача**: Добавить поддержку команд Windows (запуск .exe, чтение/запись файлов, Stop-Process) в агент.

**Контекст**: см. `Memory/GPT+Deepseek_Agent_memory.py`, переменные окружения, `cursor/rules.md`.

**Требования**:
1) Новые функции `run_exe(path, args)`, `read_file(path)`, `write_file(path, text)`, `stop_process(name_or_pid)`.
2) Маршрутизация в `respond(...)`: команды `/run`, `/read`, `/write`, `/kill`.
3) Обработка ошибок и безопасная нормализация путей.
4) Обновить `snippets.md` набором готовых примеров.
5) Тест запусков через Task «Agent: run once».

**Ожидаемый результат**: патч‑дифф + инструкции тестирования.
```

---

## 10) `.env.example` (опционально)
`D:\AI-Agent\.env.example`
```env
OPENAI_API_KEY=sk-...
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=deepseek-r1-distill-qwen-14b-abliterated-v2
AGENT_DB=D:\AI-Agent\Memory\agent_memory.sqlite
```

> При желании подключи расширение для автозагрузки `.env` (или добавь в начало скрипта парсинг `.env`).

---

## 11) Отладка и частые проблемы

### LM Studio не отвечает
- Проверь включение Local Server (OpenAI‑compatible) и порт.
- `Test-NetConnection 127.0.0.1 -Port 1234` должен быть `True`.
- `Invoke-WebRequest -Uri "$($env:LM_STUDIO_URL)/v1/models" -Method GET` должен вернуть JSON.

### Нет `OPENAI_API_KEY` в новой сессии
- Ты делал `setx OPENAI_API_KEY ...`? Открой **новое окно PowerShell**.
- Проверка: `$env:OPENAI_API_KEY` должно показывать `sk-...`.

### `py` не найден
- Используй `python` или явный путь: `D:\AI-Agent\venv\Scripts\python.exe`.

### ExecutionPolicy блокирует активацию venv
- `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force`.

### База не создаётся
- Убедись, что путь `AGENT_DB` валиден. Файл создастся при первом же вызове скрипта.

---

## 12) Дальнейшие шаги (через Cursor)
1) Добавить модуль **Windows‑команд** (/run, /read, /write, /kill).
2) Обвязка **Telegram‑бота** поверх ядра (python‑telegram‑bot 21.x).
3) **Whisper/TTS**: локально (`faster-whisper` + `sounddevice`) и/или через OpenAI.
4) Экспорт логов запросов/ответов в CSV/JSON для анализа.

---

### Контрольный мини‑скрипт запуска (Task Runner)
Можно добавить `cursor\tasks.code.json` шаг «start chat» (см. раздел 6) и запускать агент прямо из Cursor.

**Финальная проверка:**
- `Agent: run once` → отвечает.
- `/remember`, `/recall` → работают.
- Fallback тест пройден.

> Если нужна сборка отдельных патчей (дифф‑файлы) — скажи, подготовлю шаблоны PR/коммитов.

