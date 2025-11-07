# Watson Agent 2.0 - Технические детали

## Архитектура

### Компоненты системы

```
┌─────────────────┐
│   Cursor IDE    │
│  (пользователь) │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────────────────────────┐
│   FastAPI Server (port 8090)        │
│   api/fastapi_agent.py              │
│                                     │
│   /autocode/generate                │
│   /agent/respond                    │
│   /health, /version                 │
└────────┬────────────────────────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    │          │          │          │
    ↓          ↓          ↓          ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│  LLM   │ │Patcher │ │ Tester │ │ Telegram │
│ Client │ │(7 strat│ │(pytest)│ │  Notify  │
└────────┘ └────────┘ └────────┘ └──────────┘
    │
    ↓
┌─────────────────┐
│   LM Studio     │
│   port 1234     │
│                 │
│ • DeepSeek-R1   │
│ • Qwen2.5-Coder │
└─────────────────┘
```

## Механизм применения патчей

### 7-стратегий патчер

```python
def apply_patch(repo_root: str, unified_diff: str) -> tuple[bool, str]:
    # 0. Валидация структуры diff
    validate_unified_diff()
    
    # 1. Strip git metadata (diff --git, index, mode)
    base = strip_git_metadata(normalize_newlines(unified_diff))
    
    # 2. Git apply strategies (в порядке приоритета):
    strategies = [
        [],  # standard
        ["--ignore-space-change", "--ignore-whitespace"],
        # + strip a/b prefixes:
        [],
        ["--ignore-space-change", "--ignore-whitespace"],
        ["-p0"],
        ["--unidiff-zero"]
    ]
    
    # 3. FALLBACK: in-memory patch (без git)
    if all_git_strategies_failed:
        return apply_unified_diff_in_memory(repo, base)
```

### Fallback патчер (построчное применение)

```python
def _apply_unified_diff_in_memory(repo_path, diff_text):
    # 1. Парсим заголовки файлов (--- / +++)
    for old_path, new_path, hunks in parse_headers(diff_text):
        # 2. Определяем операцию
        if old_path == "/dev/null":
            create_file(new_path, extract_added_lines(hunks))
        elif new_path == "/dev/null":
            delete_file(old_path)
        else:
            # 3. Применяем построчно
            original = read_file(old_path)
            result = apply_hunks_line_by_line(original, hunks)
            write_file(old_path, result)
```

## Промпт-стратегия (Few-shot)

### Системный промпт с примерами

```
STRICT FORMAT:
- NO 'diff --git', NO 'index', NO file modes
- NO 'a/' or 'b/' prefixes

EXAMPLE 1 (add import):
--- tools/example.py
+++ tools/example.py
@@ -1,3 +1,4 @@
 import os
+import json

EXAMPLE 2 (modify):
--- config.toml
+++ config.toml
@@ -10,7 +10,7 @@
-old_value = "x"
+new_value = "y"
```

Это снижает частоту ошибок генерации на ~40%.

## Валидация diff

### Pre-check перед применением

```python
def _validate_unified_diff(txt):
    # 1. Наличие заголовков --- / +++
    if not HEADER_RE.search(txt):
        return False, "missing headers"
    
    # 2. Наличие hunks (@@ ... @@)
    if not HUNK_RE.search(txt):
        return False, "missing hunks"
    
    # 3. Проверка well-formed hunks
    for hunk in HUNK_FULL_RE.finditer(txt):
        if not hunk.group('old_start') or not hunk.group('new_start'):
            return False, "malformed hunk"
    
    # 4. Согласованность путей (для MODIFIED)
    if old != "/dev/null" and new != "/dev/null":
        if clean(old) != clean(new):
            return False, "inconsistent filenames"
    
    return True, "ok"
```

## Тестирование

### Маркеры pytest

```python
@pytest.mark.integration  # Тесты, требующие API/сервисов
def test_api_connection():
    ...
```

### Запуск

```bash
# Только юнит-тесты
pytest -q -k "not integration"

# Все тесты
pytest -q

# С отключением автоплагинов (для стабильности)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## Telegram интеграция

### Уведомления

```python
def _tg_send(msg: str) -> bool:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": msg[:4000]}
    )
```

### События

- `🧪 DRY-RUN` - задача получена, diff сгенерирован
- `🧩 PATCH FAILED TO APPLY` - все стратегии упали
- `✅ PATCH APPLIED` - патч применён, тесты прошли/упали

## Переключение моделей

### Приоритет выбора модели для diff

```
1. body.model (из HTTP запроса)
2. $env:WATSON_DIFF_MODEL (переменная окружения)
3. config.toml [models] diff_generator
4. config.toml [models] coder_model (fallback)
```

### Примеры

```powershell
# Временно на эту сессию
$env:WATSON_DIFF_MODEL = "deepseek-r1-distill-qwen-14b-abliterated-v2"

# Постоянно через config.toml
[models]
diff_generator = "deepseek-r1-distill-qwen-14b-abliterated-v2"
```

## Git интеграция

### Инициализация

```powershell
git init
git add -A
git commit -m "Initial commit"
```

### .gitignore (авто-создан)

```
__pycache__/
*.pyc
.env
.venv
venv/
api/misc/venv/
api/misc/Memory/_quarantine*/
*.log
patch.last.diff
```

## Стабильность портов

### Скрипт Start-WatsonApi.ps1

```powershell
function Stop-PortUsers($port) {
    # Находит и гасит процессы на порту
    Get-NetTCPConnection -LocalPort $port | 
        Select -ExpandProperty OwningProcess | 
        % { Stop-Process -Id $_ -Force }
}

function Wait-Health($url, $retries=30) {
    # Ждёт готовность /health до 30 попыток
    for ($i=0; $i -lt $retries; $i++) {
        if ((iwr $url -TimeoutSec 2).StatusCode -eq 200) { 
            return $true 
        }
        Start-Sleep -Milliseconds 300
    }
    return $false
}
```

## Workflow полного цикла

```
┌──────────────┐
│ Задача (text)│
└──────┬───────┘
       │
       ↓
┌─────────────────────────────────┐
│ LLM генерирует unified diff     │
│ (с few-shot промптом)           │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ Валидация diff структуры        │
│ _validate_unified_diff()        │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ Strip git metadata              │
│ (diff --git, index, mode)       │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ Git apply стратегии (6 попыток) │
│ ├─ standard                     │
│ ├─ ignore whitespace            │
│ ├─ strip a/b + retry            │
│ ├─ -p0                          │
│ └─ --unidiff-zero               │
└──────┬──────────────────────────┘
       │ FAIL?
       ↓
┌─────────────────────────────────┐
│ FALLBACK: in-memory patcher     │
│ Парсит hunks вручную            │
│ Применяет построчно без git     │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ Запуск pytest                   │
│ test_cmd из config.toml         │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│ Telegram уведомление            │
│ ✅/🧩 + логи + статус тестов    │
└─────────────────────────────────┘
```

## API Endpoints

### POST /autocode/generate

**Request:**
```json
{
  "task": "Add logging to function X",
  "repo_path": "D:\\path\\to\\repo",
  "test_cmd": "pytest -q",
  "model": "qwen2.5-coder-7b-instruct",
  "dry_run": false,
  "temperature": 0.1,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "ok": true,
  "applied": true,
  "tests_passed": true,
  "diff_len": 256,
  "logs": "...",
  "diff": "--- file.py\n+++ file.py\n..."
}
```

### POST /agent/respond

**Request:**
```json
{
  "message": "/pwd",
  "user_id": 123,
  "ctx": {}
}
```

**Response:**
```json
{
  "ok": true,
  "reply": "D:\\current\\directory"
}
```

## Производительность

- **Генерация diff:** 2-10 сек (зависит от модели)
- **Применение патча:** < 1 сек (git apply) или 1-3 сек (fallback)
- **Pytest (unit):** 10-15 сек (15 тестов)
- **Полный цикл:** ~15-30 сек

## Безопасность

- API keys/tokens хранятся в User env (не в коде)
- `.gitignore` исключает `.env`, логи, venv
- Маскирование sensitive data в логах (см. `_mask_sensitive_data`)
- Telegram токены не попадают в git

## Мониторинг

### Логи

```powershell
# API логи
Get-Content .\uvicorn_8090.out.log -Tail 100
Get-Content .\uvicorn_8090.err.log -Tail 100

# Последний применённый diff
Get-Content .\patch.last.diff
```

### Метрики

- Uptime: `/version` → `uptime_sec`
- Health: `/health` → `{"ok": true}`
- Git status: `git status --porcelain`

