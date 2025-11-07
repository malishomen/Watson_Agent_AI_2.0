# quick_commands.ps1 - Карманный набор команд для AI-Agent
# Быстрые one-liners для ежедневного использования

param(
    [ValidateSet("status", "health", "command", "pending", "approve", "logs", "processes", "restart")]
    [string]$Action = "status",
    [string]$Text = "",
    [string]$Session = "QuickCmd"
)

# Настройка UTF-8
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

# Заголовки для API
$h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }

switch ($Action) {
    "status" {
        Write-Host "🔍 СТАТУС AI-AGENT" -ForegroundColor Cyan
        Write-Host "="*40 -ForegroundColor Gray
        
        # Процессы
        $processes = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
        Write-Host "Процессы: $($processes.Count)" -ForegroundColor $(if($processes.Count -gt 0) {"Green"} else {"Red"})
        
        # Порт
        $portCheck = netstat -ano | findstr ":8088"
        Write-Host "Порт 8088: $(if($portCheck) {"Занят"} else {"Свободен"})" -ForegroundColor $(if($portCheck) {"Green"} else {"Red"})
        
        # API
        try {
            $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 3
            Write-Host "API: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "API: Недоступен" -ForegroundColor Red
        }
    }
    
    "health" {
        try {
            $health = Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 5
            Write-Host "✅ API: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "❌ API недоступен: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "command" {
        if (-not $Text) {
            Write-Host "❌ Укажите текст команды: -Text 'где я'" -ForegroundColor Red
            return
        }
        
        try {
            $body = @{ text = $Text; session = $Session } | ConvertTo-Json -Compress
            $result = Invoke-RestMethod -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec 10
            
            if ($result.ok) {
                Write-Host "✅ Команда: $($result.normalized)" -ForegroundColor Green
                Write-Host "📋 Результат:" -ForegroundColor Cyan
                Write-Host $result.result -ForegroundColor White
            } else {
                Write-Host "❌ Ошибка: $($result.result)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Ошибка выполнения: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "pending" {
        try {
            $pending = Invoke-RestMethod -Method Get http://127.0.0.1:8088/approvals/pending -Headers $h -TimeoutSec 5
            
            if ($pending.Count -eq 0) {
                Write-Host "✅ Нет ожидающих подтверждения заявок" -ForegroundColor Green
            } else {
                Write-Host "⏳ Ожидают подтверждения ($($pending.Count) заявок):" -ForegroundColor Yellow
                foreach ($item in $pending) {
                    Write-Host "🆔 $($item.id)" -ForegroundColor Cyan
                    Write-Host "📝 $($item.action)" -ForegroundColor Gray
                    Write-Host "⏰ $($item.created_at)" -ForegroundColor Gray
                    Write-Host "✅ /approve $($item.id)" -ForegroundColor Green
                    Write-Host ""
                }
            }
        } catch {
            Write-Host "❌ Ошибка получения pending: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "approve" {
        if (-not $Text) {
            Write-Host "❌ Укажите ID для подтверждения: -Text 'AP-1234567890'" -ForegroundColor Red
            return
        }
        
        try {
            $body = @{ text = "/approve $Text"; session = $Session } | ConvertTo-Json -Compress
            $result = Invoke-RestMethod -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec 10
            
            if ($result.ok) {
                Write-Host "✅ Заявка $Text подтверждена" -ForegroundColor Green
                Write-Host "📋 Результат:" -ForegroundColor Cyan
                Write-Host $result.result -ForegroundColor White
            } else {
                Write-Host "❌ Ошибка подтверждения: $($result.result)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Ошибка подтверждения: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    "logs" {
        $logFile = "D:\AI-Agent\Memory\ops_log.csv"
        if (Test-Path $logFile) {
            Write-Host "📋 Последние операции:" -ForegroundColor Cyan
            Get-Content $logFile | Select-Object -Last 10 | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
        } else {
            Write-Host "❌ Файл логов не найден" -ForegroundColor Red
        }
    }
    
    "processes" {
        Write-Host "🔍 Процессы Python/Uvicorn:" -ForegroundColor Cyan
        $processes = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
        if ($processes) {
            $processes | Format-Table ProcessName, Id, CPU, WorkingSet -AutoSize
        } else {
            Write-Host "❌ Процессы не найдены" -ForegroundColor Red
        }
    }
    
    "restart" {
        Write-Host "🔄 Перезапуск системы..." -ForegroundColor Yellow
        & "D:\AI-Agent\scripts\incident_playbook.ps1" -Action restart
    }
}

Write-Host "`n💡 Примеры использования:" -ForegroundColor Cyan
Write-Host ".\scripts\quick_commands.ps1 -Action status" -ForegroundColor Gray
Write-Host ".\scripts\quick_commands.ps1 -Action command -Text 'где я'" -ForegroundColor Gray
Write-Host ".\scripts\quick_commands.ps1 -Action pending" -ForegroundColor Gray
Write-Host ".\scripts\quick_commands.ps1 -Action approve -Text 'AP-1234567890'" -ForegroundColor Gray
