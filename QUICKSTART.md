# Watson Agent 2.0 - Быстрый старт

## 🚀 Запуск системы (3 команды)

### 1. Установка переменных окружения (один раз)

```powershell
# В PowerShell от имени пользователя
[Environment]::SetEnvironmentVariable('TELEGRAM_TOKEN', 'ваш_токен_бота', 'User')
[Environment]::SetEnvironmentVariable('TELEGRAM_CHAT_ID', 'ваш_chat_id', 'User')
[Environment]::SetEnvironmentVariable('WATSON_API_BASE', 'http://127.0.0.1:8090', 'User')
```

### 2. Запуск LM Studio

- Откройте LM Studio
- Загрузите модели:
  - `deepseek-r1-distill-qwen-14b-abliterated-v2` (reasoning)
  - `qwen2.5-coder-7b-instruct` (diff generation)
- Запустите локальный сервер на порту 1234

### 3. Запуск Watson API

```powershell
cd D:\projects\Ai-Agent_Watson\Watson_Agent_2.0
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-WatsonApi.ps1 -Port 8090
```

Дождитесь сообщения: `API is ready on http://127.0.0.1:8090`

---

## 📝 Отправка задач

### Через PowerShell скрипт

```powershell
.\Send-Task.ps1 -Task "Add logging to calculate_total function in utils/math.py"
```

### Через HTTP запрос

```powershell
$body = @{
  task = "Refactor user authentication to use async/await"
  repo_path = "D:\projects\Ai-Agent_Watson\Watson_Agent_2.0"
  test_cmd = 'py -3.11 -m pytest -q -k "not integration"'
  dry_run = $false
} | ConvertTo-Json -Depth 7

Invoke-WebRequest "http://127.0.0.1:8090/autocode/generate" `
  -Method POST -ContentType "application/json" -Body $body | 
  Select-Object -ExpandProperty Content
```

### Из Cursor (с интеграцией)

1. Выделите текст задачи в редакторе
2. Нажмите `Ctrl+Shift+P` → `Tasks: Run Task`
3. Выберите:
   - **Send to Agent (DryRun)** - получить diff без применения
   - **Send to Agent (Apply+Test)** - применить + запустить тесты

---

## 🔧 Настройки

### Переключение модели для генерации diff

Если Qwen генерирует некорректные diff'ы:

```powershell
$env:WATSON_DIFF_MODEL = "deepseek-r1-distill-qwen-14b-abliterated-v2"
```

Или измените `config.toml`:

```toml
[models]
diff_generator = "deepseek-r1-distill-qwen-14b-abliterated-v2"
```

### Настройка test_cmd

В `config.toml`:

```toml
test_cmd = 'py -3.11 -m pytest -q -k "not integration"'
```

---

## 📊 Проверка статуса

### Health check

```powershell
Invoke-WebRequest http://127.0.0.1:8090/health | Select-Object -ExpandProperty Content
# {"ok":true}
```

### Version info

```powershell
Invoke-WebRequest http://127.0.0.1:8090/version | Select-Object -ExpandProperty Content
# {"service":"watson-agent","uptime_sec":123.4,"reasoning_model":"...","coder_model":"..."}
```

### Запуск тестов вручную

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
py -3.11 -m pytest -q -k "not integration"
```

---

## 🛠️ Troubleshooting

### API не запускается

```powershell
# Проверьте занятость порта
Get-NetTCPConnection -State Listen -LocalPort 8090 -ErrorAction SilentlyContinue

# Убейте старые процессы
Get-Process | ? { $_.ProcessName -match "python|uvicorn" } | Stop-Process -Force

# Перезапустите
pwsh -File .\scripts\Start-WatsonApi.ps1 -Port 8090
```

### Патч не применяется

Система автоматически пробует 7 стратегий:
1. git apply (standard)
2. git apply --ignore-whitespace
3. git apply после strip a/b prefixes
4. git apply -p0
5. git apply --unidiff-zero
6. **Fallback in-memory** (парсинг hunks вручную)

Если все стратегии падают, проверьте `patch.last.diff` и логи.

### Telegram не отправляет уведомления

```powershell
# Проверьте переменные
[Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
[Environment]::GetEnvironmentVariable('TELEGRAM_CHAT_ID','User')

# Перезапустите API
pwsh -File .\scripts\Start-WatsonApi.ps1 -Port 8090
```

---

## 📁 Структура проекта

```
Watson_Agent_2.0/
├── api/
│   ├── fastapi_agent.py      # Основное FastAPI приложение
│   ├── agent.py               # Логика agent.respond
│   └── parsers/               # NLP парсеры команд
├── tools/
│   ├── llm_client.py          # Клиент для LM Studio
│   ├── patcher.py             # 7-стратегий патчер (+ fallback)
│   └── tester.py              # Запуск pytest
├── utils/
│   ├── prompts.py             # Few-shot промпты для LLM
│   ├── safe_call.py           # Обёртка для respond
│   └── env_check.py           # Проверка env переменных
├── tests/                     # Тесты (unit + integration)
├── scripts/
│   └── Start-WatsonApi.ps1    # Умный запуск API
├── config.toml                # Конфигурация моделей
├── Send-Task.ps1              # Отправка задач в автокодер
└── .cursor/
    └── tasks.code.json        # Интеграция с Cursor
```

---

## 🎯 Workflow

1. **Запустите API** (один раз): `pwsh -File .\scripts\Start-WatsonApi.ps1 -Port 8090`
2. **Отправьте задачу**: `.\Send-Task.ps1 -Task "ваша задача"`
3. **Проверьте результат** в Telegram
4. **Просмотрите изменения**: `git diff`
5. **Закоммитьте**: `git add -A && git commit -m "описание"`

Система работает автономно: генерирует diff → применяет (fallback если нужно) → тестирует → отчитывается в Telegram!

