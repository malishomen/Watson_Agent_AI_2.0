# STEP 4 — Cursor → Agent API (прямое управление через HTTP)

> **Зачем:** запускать и контролировать вашего локального ПК‑агента **напрямую из Cursor** с помощью готовых задач (Run Task), которые бьют в FastAPI‑эндпоинты.  
> **Философия:** *мы — МОЗГ*, агент — *ИСПОЛНИТЕЛЬ*. Cursor — «пульт оператора».  
> **Как работает:** вы один раз вводите `API URL` и `API SECRET` → задачи используют их в текущем терминале Cursor и **не** хранят секреты в файлах.

---

## 0) Предпосылки

- Шаги **2–3** выполнены: агент с командами `/run /read /write /kill /cd /pwd /approve`, **WORKDIR‑персист**, `ProjectSpec.yml`, `run_project.py`, **FastAPI** запущен (локально на `127.0.0.1:8088`).  
- Активирован `venv`: `D:\AI-Agent\venv\Scripts\Activate.ps1`  
- LM Studio поднят (модель настроена).

Структура (важное):
```
D:\AI-Agent
├─ Memory\GPT+Deepseek_Agent_memory.py
├─ api\fastapi_agent.py
├─ run_project.py
├─ ProjectSpec.yml
└─ cursor\        ← здесь храним скрипты и tasks
```

---

## 1) Создаём скрипт запроса API‑параметров (PowerShell)

**Файл:** `D:\AI-Agent\cursor\prompt_api_vars.ps1` — спрашивает URL и секрет, выставляет их **в текущей сессии**:

```powershell
# cursor\prompt_api_vars.ps1
param(
  [string]$DefaultUrl = "http://127.0.0.1:8088"
)

Write-Host "=== Настройка подключения к Agent API ===" -ForegroundColor Cyan

# URL (видно)
$apiUrl = Read-Host "Введите API URL (Enter для значения по умолчанию: $DefaultUrl)"
if ([string]::IsNullOrWhiteSpace($apiUrl)) { $apiUrl = $DefaultUrl }

# SECRET (скрытый ввод)
$sec = Read-Host -AsSecureString "Введите API SECRET (ввод скрыт)"
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try {
  $apiSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

# В эту сессию PowerShell (не навсегда)
$env:AGENT_API_URL = $apiUrl
$env:AGENT_API_SECRET = $apiSecret

Write-Host ("AGENT_API_URL = " + $env:AGENT_API_URL) -ForegroundColor Green
if ($env:AGENT_API_SECRET) {
  Write-Host ("AGENT_API_SECRET = " + $env:AGENT_API_SECRET.Substring(0,5) + "...") -ForegroundColor Green
} else {
  Write-Host "AGENT_API_SECRET не задан!" -ForegroundColor Red
  exit 1
}
```

> Скрипт **не** пишет секреты в реестр/файлы, действует только в текущем терминале Cursor.

---

## 2) Обновляем `cursor\tasks.code.json` — готовые задачи

**Файл:** `D:\AI-Agent\cursor\tasks.code.json`  
Если файла нет — создайте. Если есть — **добавьте** блоки ниже. Каждая задача вызывается через **Run Task** в Cursor.

> **Подсказка:** путь к PowerShell в командах прописан коротко (`powershell ...`). Этого достаточно внутри терминала Windows.

```json
[
  {
    "title": "API: prompt credentials",
    "description": "Запросить API URL и SECRET и выставить их в текущей сессии",
    "steps": [
      { "type": "terminal", "command": "powershell -ExecutionPolicy Bypass -File .\\cursor\\prompt_api_vars.ps1" }
    ]
  },
  {
    "title": "API: health (ожидаем 200)",
    "description": "GET /health (без секрета)",
    "steps": [
      { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri \"$env:AGENT_API_URL/health\" -Method GET | Select-Object -Expand Content" }
    ]
  },
  {
    "title": "API: workdir (без секрета → 401)",
    "description": "GET /workdir без заголовка",
    "steps": [
      { "type": "terminal", "command": "powershell try { (Invoke-WebRequest -Uri \"$env:AGENT_API_URL/workdir\" -Method GET).StatusCode } catch { $_.Exception.Response.StatusCode }" }
    ]
  },
  {
    "title": "API: workdir (c секретом → pwd)",
    "description": "GET /workdir с x-agent-secret",
    "steps": [
      { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri \"$env:AGENT_API_URL/workdir\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method GET | Select-Object -Expand Content" }
    ]
  },
  {
    "title": "API: cd → pwd",
    "description": "POST /cd, затем GET /workdir",
    "steps": [
      { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri \"$env:AGENT_API_URL/cd\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method POST -Body (@{ session='Danil-PC'; path='D:\\\\AI-Agent\\\\Memory' } | ConvertTo-Json) -ContentType 'application/json' | Select-Object -Expand Content" },
      { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri \"$env:AGENT_API_URL/workdir\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method GET | Select-Object -Expand Content" }
    ]
  },
  {
    "title": "API: command /notes",
    "description": "POST /command с /notes",
    "steps": [
      { "type": "terminal", "command": "powershell (Invoke-WebRequest -Uri \"$env:AGENT_API_URL/command\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method POST -Body (@{ session='Danil-PC'; command='/notes' } | ConvertTo-Json) -ContentType 'application/json').Content | ConvertFrom-Json | Select -Expand stdout" }
    ]
  },
  {
    "title": "API: run ProjectSpec.yml",
    "description": "POST /run-spec и печать stdout",
    "steps": [
      { "type": "terminal", "command": "powershell (Invoke-WebRequest -Uri \"$env:AGENT_API_URL/run-spec\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method POST -Body (@{ spec_path='D:\\\\AI-Agent\\\\ProjectSpec.yml' } | ConvertTo-Json) -ContentType 'application/json').Content | ConvertFrom-Json | Select -Expand stdout" }
    ]
  },
  {
    "title": "API: approve (ручной ввод AP-ID)",
    "description": "Подтвердить опасное действие по AP-ID",
    "steps": [
      { "type": "terminal", "command": "powershell $ap=Read-Host 'Введите approval ID (например AP-1234567890)'; (Invoke-WebRequest -Uri \"$env:AGENT_API_URL/approve\" -Headers @{ 'x-agent-secret'=$env:AGENT_API_SECRET } -Method POST -Body (@{ session='Danil-PC'; approval_id=$ap } | ConvertTo-Json) -ContentType 'application/json').Content | ConvertFrom-Json | Select -Expand stdout" }
    ]
  }
]
```

> **Безопасность:** секреты берутся из переменных окружения текущей сессии (см. шаг 1) и **не** пишутся в tasks‑файл.

---

## 3) Quality‑of‑Life (опционально)

### 3.1 PowerShell в UTF‑8 по умолчанию (чтобы кириллица не «ломалась»)
```powershell
notepad $PROFILE
```
В профиль добавьте:
```powershell
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
```

### 3.2 Быстрый alias для curl.exe
```powershell
Set-Alias curlx "$env:SystemRoot\System32\curl.exe"
```
Проверка:
```powershell
curlx -s -H "x-agent-secret: $env:AGENT_API_SECRET" "$env:AGENT_API_URL/workdir"
```

---

## 4) Чек‑лист прохождения Step 4 (в Cursor → Run Task)

1. **API: prompt credentials** — введите URL и SECRET.  
2. **API: health** — ожидаем `{"status":"ok"}`.  
3. **API: workdir (без секрета)** — код **401 Unauthorized**.  
4. **API: workdir (с секретом)** — `stdout` содержит путь (pwd).  
5. **API: cd → pwd** — смена и сохранение `WORKDIR`.  
6. **API: command /notes** — печать последних заметок.  
7. **API: run ProjectSpec.yml** — пошаговый прогон, будет AP‑ID на шаге вне whitelist.  
8. **API: approve** — введите `AP-...` и подтвердите действие.

---

## 5) Troubleshooting (быстрые решения)

- **401 Unauthorized** → проверьте, что задачи с секретом действительно запускаются **после** `API: prompt credentials`; секрет корректен, FastAPI проверяет `x-agent-secret`.  
- **(7) 404 Not Found для run-spec** → проверьте путь `D:\AI-Agent\ProjectSpec.yml`.  
- **ECONNREFUSED/таймаут** → поднимите API:
  ```powershell
  cd D:\AI-Agent
  D:\AI-Agent\venv\Scripts\Activate.ps1
  uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
  ```
- **Кодировка «кракозябры»** → включите UTF‑8 профиль (см. §3.1).  
- **Проблемы с кавычками** в путях → берите пути в двойные кавычки `"D:\\AI-Agent\\Memory\\file.txt"` и удваивайте обратные слэши в JSON.

---

## 6) Что дальше (Step 5 — по желанию)

- **Operator UI (FastAPI + Jinja/HTMX)**: `/ui/logs`, `/ui/specs`, `/ui/run` (SSE‑лог), `/ui/approvals`.  
- **Роли и политики:** `readonly / operator / admin` + правила по командам/каталогам.  
- **Планировщик:** RRULE/cron для `ProjectSpec` + уведомления в Telegram.

Скажете «Стартуем UI/Роли/Планировщик» — подготовлю пакет и отдельные Cursor‑таски.
