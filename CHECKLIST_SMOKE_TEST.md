# 🔥 Watson Agent 2.0 - Smoke Test Checklist

Быстрая проверка всей системы за 5 минут.

## ✅ Pre-flight (перед запуском)

```powershell
# 1. Проверка Python
py -3.11 --version
# Expected: Python 3.11.x

# 2. Проверка переменных окружения
[Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
[Environment]::GetEnvironmentVariable('TELEGRAM_CHAT_ID','User')
# Expected: не пусто

# 3. LM Studio запущен?
Invoke-WebRequest http://127.0.0.1:1234/v1/models | Select-Object -ExpandProperty Content
# Expected: JSON со списком моделей
```

## ✅ Шаг 1: Запуск API

```powershell
cd D:\projects\Ai-Agent_Watson\Watson_Agent_2.0
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-WatsonApi.ps1 -Port 8090
```

**Ожидаемый результат:**
```
API is ready on http://127.0.0.1:8090 (log: ...\uvicorn_8090.out.log)
```

## ✅ Шаг 2: Health check

```powershell
Invoke-WebRequest http://127.0.0.1:8090/health | Select-Object -ExpandProperty Content
```

**Ожидаемый результат:**
```json
{"ok":true}
```

## ✅ Шаг 3: Version info

```powershell
Invoke-WebRequest http://127.0.0.1:8090/version | Select-Object -ExpandProperty Content
```

**Ожидаемый результат:**
```json
{
  "service":"watson-agent",
  "uptime_sec":12.3,
  "reasoning_model":"deepseek-r1-distill-qwen-14b-abliterated-v2",
  "coder_model":"qwen2.5-coder-7b-instruct"
}
```

## ✅ Шаг 4: Юнит-тесты

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
py -3.11 -m pytest -q -k "not integration"
```

**Ожидаемый результат:**
```
15 passed, 6 skipped, 5 deselected, 6 warnings in 11.XX s
```

## ✅ Шаг 5: DRY-RUN автокодера

```powershell
$body = @{
  task = "Test dry-run: validate diff generation"
  repo_path = (Get-Location).Path
  dry_run = $true
} | ConvertTo-Json -Depth 7

Invoke-WebRequest http://127.0.0.1:8090/autocode/generate `
  -Method POST -ContentType "application/json" -Body $body `
  -TimeoutSec 120 | Select-Object -ExpandProperty Content
```

**Ожидаемый результат:**
```json
{
  "ok": true,
  "applied": false,
  "tests_passed": null,
  "diff_len": 200,
  "logs": "dry-run",
  "diff": "--- file.py\n+++ file.py\n..."
}
```

**Telegram:** должно прийти `🧪 DRY-RUN`

## ✅ Шаг 6: Полный цикл (Apply + Test)

```powershell
git checkout utils/safe_call.py  # Откатываем для чистого теста

$body = @{
  task = "Add one-line comment '# Test comment' at top of utils/safe_call.py"
  repo_path = (Get-Location).Path
  dry_run = $false
  temperature = 0.1
} | ConvertTo-Json -Depth 7

$resp = Invoke-WebRequest http://127.0.0.1:8090/autocode/generate `
  -Method POST -ContentType "application/json" -Body $body `
  -TimeoutSec 240

$json = $resp.Content | ConvertFrom-Json
Write-Output "Applied: $($json.applied)"
Write-Output "Tests: $($json.tests_passed)"
```

**Ожидаемый результат:**
```
Applied: True
Tests: True
```

**Telegram:** должно прийти `✅ PATCH APPLIED` + статус тестов

## ✅ Шаг 7: Проверка изменений

```powershell
git diff utils/safe_call.py
```

**Ожидаемый результат:**
```diff
+# Test comment
 import inspect
```

## ✅ Шаг 8: Откат и финализация

```powershell
git checkout utils/safe_call.py
git status
```

**Ожидаемый результат:**
```
On branch master
nothing to commit, working tree clean
```

## 🎯 Критерии успеха

- [ ] API запустился на 8090
- [ ] /health возвращает `{"ok":true}`
- [ ] Юнит-тесты: 15 passed
- [ ] DRY-RUN вернул diff
- [ ] Telegram получил уведомление DRY-RUN
- [ ] Полный цикл: `applied=true, tests_passed=true`
- [ ] Telegram получил уведомление PATCH APPLIED
- [ ] git diff показывает изменения
- [ ] Лог содержит `[fallback in-memory]` (если git apply упал)

## 🔴 Если что-то упало

### API не запускается

```powershell
# Проверьте логи
Get-Content .\uvicorn_8090.err.log -Tail 50

# Убейте старые процессы
Get-Process | ? { $_.ProcessName -match "python" } | Stop-Process -Force

# Перезапустите
pwsh -File .\scripts\Start-WatsonApi.ps1 -Port 8090
```

### Патч не применился (applied=false)

```powershell
# Проверьте последний diff
Get-Content .\patch.last.diff

# Если в логах нет [fallback in-memory], значит код не обновлён
# Перезапустите API
```

### Тесты упали (tests_passed=false)

```powershell
# Запустите вручную для детального вывода
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
py -3.11 -m pytest -v -k "not integration"
```

### Telegram не получает уведомления

```powershell
# Проверьте токены
[Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
[Environment]::GetEnvironmentVariable('TELEGRAM_CHAT_ID','User')

# Проверьте доступность API Telegram
$token = [Environment]::GetEnvironmentVariable('TELEGRAM_TOKEN','User')
Invoke-WebRequest "https://api.telegram.org/bot$token/getMe"
```

## 📋 Финальная проверка

Если все 8 шагов прошли зелёными — **система полностью готова к работе**! 🎉

### Быстрая проверка одной командой

```powershell
$ok = @(
  (iwr http://127.0.0.1:8090/health).StatusCode -eq 200,
  (py -3.11 -m pytest -q -k "not integration" 2>&1 | Select-String "passed").Length -gt 0
) -notcontains $false

if ($ok) { 
  Write-Host "✅ Система готова!" -ForegroundColor Green 
} else { 
  Write-Host "❌ Проверьте логи" -ForegroundColor Red 
}
```

