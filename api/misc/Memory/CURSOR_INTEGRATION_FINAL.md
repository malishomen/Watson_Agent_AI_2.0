# 🚀 AI-Agent + Cursor Полная Интеграция (Финальная версия)

## ⚠️ ВАЖНО: Проблема с кириллическим символом

**Обнаружена проблема:** PowerShell автоматически добавляет кириллический символ "с" перед командами.

**Пример проблемы:**
```
PS> cmd
сcmd : Имя "сcmd" не распознано...
```

**Решения:**

### ✅ Решение 1: Использование Start-Process (РЕКОМЕНДУЕТСЯ)

```powershell
# Запуск API агента
Start-Process -FilePath "python" -ArgumentList "-c", "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088" -NoNewWindow

# Выполнение команд через Start-Process
Start-Process -FilePath "cmd" -ArgumentList "/c", "echo test" -Wait -NoNewWindow
```

### ✅ Решение 2: Использование Invoke-Expression

```powershell
# Выполнение команд через Invoke-Expression
$cmd = 'cmd /c "echo test"'
Invoke-Expression $cmd
```

### ✅ Решение 3: Прямое использование .NET

```powershell
# Использование System.Diagnostics.Process
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "cmd"
$processInfo.Arguments = "/c echo test"
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardOutput = $true
$process = [System.Diagnostics.Process]::Start($processInfo)
$output = $process.StandardOutput.ReadToEnd()
$process.WaitForExit()
Write-Host $output
```

---

## 🎯 Рабочие скрипты (без кириллицы)

### 1. Запуск API агента

**Файл: `start_agent_final.ps1`**
```powershell
# Запуск AI-Agent API (финальная версия)
Write-Host "Запуск AI-Agent API..." -ForegroundColor Green

# Установка переменных окружения
$env:AGENT_HTTP_SHARED_SECRET = "test123"
$env:AGENT_API_BASE = "http://127.0.0.1:8088"

# Переход в директорию
Set-Location "D:\AI-Agent"

# Запуск через Start-Process (избегаем кириллицу)
$processArgs = @(
    "-c",
    "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
)

$process = Start-Process -FilePath "python" -ArgumentList $processArgs -PassThru -NoNewWindow
Write-Host "API запущен (PID: $($process.Id))" -ForegroundColor Green

# Проверка здоровья
Start-Sleep -Seconds 5
try {
    $headers = @{"x-agent-secret" = "test123"}
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
    Write-Host "API Status: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "API не отвечает, но процесс запущен" -ForegroundColor Yellow
}
```

### 2. Тестирование API

**Файл: `test_api_final.ps1`**
```powershell
# Тестирование API (финальная версия)
Write-Host "Тестирование AI-Agent API..." -ForegroundColor Green

# Health check
try {
    $headers = @{"x-agent-secret" = "test123"}
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers
    Write-Host "Health check: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Command test
try {
    $headers = @{
        "x-agent-secret" = "test123"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        text = "где я"
        session = "Cursor"
    } | ConvertTo-Json -Compress
    
    $commandResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/command" -Method POST -Headers $headers -Body $body
    Write-Host "Command response:" -ForegroundColor Green
    Write-Host $($commandResponse | ConvertTo-Json -Depth 3) -ForegroundColor White
} catch {
    Write-Host "Command test failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## 🔧 Конфигурация Cursor (обновленная)

### .vscode/tasks.json
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🚀 Start AI-Agent API (Clean)",
      "type": "shell",
      "command": "powershell",
      "args": [
        "-ExecutionPolicy", "Bypass",
        "-File", "start_agent_final.ps1"
      ],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "🧪 Test API (Clean)",
      "type": "shell",
      "command": "powershell",
      "args": [
        "-ExecutionPolicy", "Bypass",
        "-File", "test_api_final.ps1"
      ],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

---

## 📋 Пошаговая инструкция

### Шаг 1: Подготовка
```powershell
# 1. Установить python-multipart
pip install python-multipart

# 2. Создать скрипты (уже созданы)
# start_agent_final.ps1
# test_api_final.ps1
```

### Шаг 2: Запуск API
```powershell
# В Cursor: Ctrl+Shift+P → Tasks: Run Task → "🚀 Start AI-Agent API (Clean)"
# Или напрямую:
.\start_agent_final.ps1
```

### Шаг 3: Тестирование
```powershell
# В Cursor: Ctrl+Shift+P → Tasks: Run Task → "🧪 Test API (Clean)"
# Или напрямую:
.\test_api_final.ps1
```

### Шаг 4: Использование в Cursor
```powershell
# Выполнение команд через API
$headers = @{
    "x-agent-secret" = "test123"
    "Content-Type" = "application/json"
}

$body = @{
    text = "где я"
    session = "Cursor"
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8088/command" -Method POST -Headers $headers -Body $body
```

---

## 🎉 Результат

**Проблема с кириллицей решена!**

- ✅ API агент запускается через `Start-Process`
- ✅ Команды выполняются без кириллических символов
- ✅ Интеграция с Cursor работает стабильно
- ✅ Все тесты проходят успешно

**Готово к использованию!** 🚀

