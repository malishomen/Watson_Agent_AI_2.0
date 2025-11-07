# incident_playbook.ps1 - Инцидент-плейбук для AI-Agent
param(
    [ValidateSet("diagnose", "restart", "full-reset", "status")]
    [string]$Action = "diagnose"
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "🚨 ИНЦИДЕНТ-ПЛЕЙБУК AI-AGENT" -ForegroundColor Red
Write-Host "Время: $timestamp" -ForegroundColor Gray
Write-Host "Действие: $Action" -ForegroundColor Cyan

switch ($Action) {
    "diagnose" {
        Write-Host "`n🔍 ДИАГНОСТИКА СИСТЕМЫ" -ForegroundColor Yellow
        Write-Host "="*50 -ForegroundColor Gray
        
        # 1) Проверка процессов
        Write-Host "`n1️⃣ Процессы Python/Uvicorn:" -ForegroundColor Cyan
        $processes = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
        if ($processes) {
            $processes | Format-Table ProcessName, Id, CPU, WorkingSet -AutoSize
        } else {
            Write-Host "❌ Процессы не найдены" -ForegroundColor Red
        }
        
        # 2) Проверка порта
        Write-Host "`n2️⃣ Порт 8088:" -ForegroundColor Cyan
        $portCheck = netstat -ano | findstr ":8088"
        if ($portCheck) {
            Write-Host "✅ Порт занят:" -ForegroundColor Green
            $portCheck | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        } else {
            Write-Host "❌ Порт свободен" -ForegroundColor Red
        }
        
        # 3) Проверка API
        Write-Host "`n3️⃣ API Health Check:" -ForegroundColor Cyan
        try {
            $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 5
            Write-Host "✅ API отвечает: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "❌ API недоступен: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        # 4) Проверка переменных окружения
        Write-Host "`n4️⃣ Переменные окружения:" -ForegroundColor Cyan
        if ($env:AGENT_HTTP_SHARED_SECRET) {
            Write-Host "✅ AGENT_HTTP_SHARED_SECRET: установлен ($($env:AGENT_HTTP_SHARED_SECRET.Length) символов)" -ForegroundColor Green
        } else {
            Write-Host "❌ AGENT_HTTP_SHARED_SECRET: не установлен" -ForegroundColor Red
        }
        
        # 5) Проверка файлов
        Write-Host "`n5️⃣ Критические файлы:" -ForegroundColor Cyan
        $criticalFiles = @(
            "D:\AI-Agent\api\fastapi_agent_fixed.py",
            "D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py",
            "D:\AI-Agent\Memory\agent_memory.sqlite"
        )
        
        foreach ($file in $criticalFiles) {
            if (Test-Path $file) {
                $size = (Get-Item $file).Length
                Write-Host "✅ $file ($size байт)" -ForegroundColor Green
            } else {
                Write-Host "❌ $file - НЕ НАЙДЕН" -ForegroundColor Red
            }
        }
    }
    
    "restart" {
        Write-Host "`n🔄 ПЕРЕЗАПУСК СИСТЕМЫ" -ForegroundColor Yellow
        Write-Host "="*50 -ForegroundColor Gray
        
        # 1) Остановка процессов
        Write-Host "`n1️⃣ Остановка процессов..." -ForegroundColor Cyan
        $processes = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
        if ($processes) {
            $processes | Stop-Process -Force
            Write-Host "✅ Остановлено $($processes.Count) процессов" -ForegroundColor Green
        } else {
            Write-Host "ℹ️ Процессы не найдены" -ForegroundColor Gray
        }
        
        # 2) Ожидание освобождения порта
        Write-Host "`n2️⃣ Ожидание освобождения порта..." -ForegroundColor Cyan
        Start-Sleep 3
        
        # 3) Настройка окружения
        Write-Host "`n3️⃣ Настройка окружения..." -ForegroundColor Cyan
        chcp 65001 | Out-Null
        $OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONUTF8 = "1"
        Write-Host "✅ UTF-8 настроен" -ForegroundColor Green
        
        # 4) Активация venv
        Write-Host "`n4️⃣ Активация виртуального окружения..." -ForegroundColor Cyan
        if (Test-Path "D:\AI-Agent\venv\Scripts\Activate.ps1") {
            & "D:\AI-Agent\venv\Scripts\Activate.ps1"
            Write-Host "✅ Виртуальное окружение активировано" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Виртуальное окружение не найдено" -ForegroundColor Yellow
        }
        
        # 5) Запуск API
        Write-Host "`n5️⃣ Запуск API..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList @(
            "-NoProfile", "-Command",
            "cd D:\AI-Agent; D:\AI-Agent\venv\Scripts\Activate.ps1; `$env:AGENT_HTTP_SHARED_SECRET='$env:AGENT_HTTP_SHARED_SECRET'; uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
        )
        
        Write-Host "✅ API запущен в фоне" -ForegroundColor Green
        
        # 6) Проверка запуска
        Write-Host "`n6️⃣ Проверка запуска..." -ForegroundColor Cyan
        Start-Sleep 5
        try {
            $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 10
            Write-Host "✅ API успешно запущен: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "❌ API не отвечает после перезапуска" -ForegroundColor Red
        }
    }
    
    "full-reset" {
        Write-Host "`n💥 ПОЛНЫЙ СБРОС СИСТЕМЫ" -ForegroundColor Red
        Write-Host "="*50 -ForegroundColor Gray
        Write-Host "⚠️ ВНИМАНИЕ: Это удалит все процессы и очистит порты!" -ForegroundColor Yellow
        
        # 1) Остановка всех процессов
        Write-Host "`n1️⃣ Остановка всех процессов..." -ForegroundColor Cyan
        Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" } | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "✅ Все процессы остановлены" -ForegroundColor Green
        
        # 2) Очистка портов
        Write-Host "`n2️⃣ Очистка портов..." -ForegroundColor Cyan
        Start-Sleep 3
        
        # 3) Сброс переменных окружения
        Write-Host "`n3️⃣ Сброс переменных окружения..." -ForegroundColor Cyan
        $env:AGENT_HTTP_SHARED_SECRET = "6334bbf0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2"
        chcp 65001 | Out-Null
        $OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONUTF8 = "1"
        Write-Host "✅ Переменные окружения сброшены" -ForegroundColor Green
        
        # 4) Активация venv
        Write-Host "`n4️⃣ Активация виртуального окружения..." -ForegroundColor Cyan
        if (Test-Path "D:\AI-Agent\venv\Scripts\Activate.ps1") {
            & "D:\AI-Agent\venv\Scripts\Activate.ps1"
            Write-Host "✅ Виртуальное окружение активировано" -ForegroundColor Green
        }
        
        # 5) Запуск API
        Write-Host "`n5️⃣ Запуск API..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList @(
            "-NoProfile", "-Command",
            "cd D:\AI-Agent; D:\AI-Agent\venv\Scripts\Activate.ps1; `$env:AGENT_HTTP_SHARED_SECRET='$env:AGENT_HTTP_SHARED_SECRET'; uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level debug"
        )
        
        Write-Host "✅ API запущен в режиме отладки" -ForegroundColor Green
    }
    
    "status" {
        Write-Host "`n📊 СТАТУС СИСТЕМЫ" -ForegroundColor Yellow
        Write-Host "="*50 -ForegroundColor Gray
        
        # Быстрая проверка
        $processes = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
        $portCheck = netstat -ano | findstr ":8088"
        
        Write-Host "Процессы: $($processes.Count)" -ForegroundColor $(if($processes.Count -gt 0) {"Green"} else {"Red"})
        Write-Host "Порт 8088: $(if($portCheck) {"Занят"} else {"Свободен"})" -ForegroundColor $(if($portCheck) {"Green"} else {"Red"})
        
        try {
            $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 3
            Write-Host "API: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "API: Недоступен" -ForegroundColor Red
        }
    }
}

Write-Host "`n🎯 Инцидент-плейбук завершен: $Action" -ForegroundColor Green
Write-Host "💡 Для диагностики: .\scripts\incident_playbook.ps1 -Action diagnose" -ForegroundColor Cyan
Write-Host "💡 Для перезапуска: .\scripts\incident_playbook.ps1 -Action restart" -ForegroundColor Cyan
Write-Host "💡 Для полного сброса: .\scripts\incident_playbook.ps1 -Action full-reset" -ForegroundColor Cyan
