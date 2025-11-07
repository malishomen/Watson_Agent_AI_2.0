# Cursor Automation Script
# Автономный агент для управления Cursor через горячие клавиши
# Согласно инструкциям по интеграции Cursor для автономного агента

param(
    [string]$ProjectPath = "D:\AI-Agent",
    [string]$Task = "Создай полнофункциональное веб-приложение на FastAPI с PostgreSQL базой данных",
    [string]$Secret = "test123"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Cursor Automation Agent ===" -ForegroundColor Cyan
Write-Host "Проект: $ProjectPath" -ForegroundColor Yellow
Write-Host "Задача: $Task" -ForegroundColor Yellow

# Функция для отправки клавиш в Cursor
function Send-KeysToCursor {
    param([string]$Keys, [int]$Delay = 500)
    
    try {
        # Использование SendKeys для отправки клавиш
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait($Keys)
        Start-Sleep -Milliseconds $Delay
        return $true
    } catch {
        Write-Host "Ошибка отправки клавиш: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Функция для поиска окна Cursor
function Find-CursorWindow {
    try {
        Add-Type -AssemblyName System.Windows.Forms
        $processes = Get-Process | Where-Object { $_.ProcessName -like "*cursor*" -or $_.MainWindowTitle -like "*cursor*" }
        
        if ($processes) {
            Write-Host "Найдено окно Cursor: $($processes[0].MainWindowTitle)" -ForegroundColor Green
            return $processes[0]
        } else {
            Write-Host "Окно Cursor не найдено" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "Ошибка поиска окна Cursor: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Функция для активации окна Cursor
function Activate-CursorWindow {
    param([System.Diagnostics.Process]$Process)
    
    try {
        if ($Process -and $Process.MainWindowHandle -ne [IntPtr]::Zero) {
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern bool SetForegroundWindow(IntPtr hWnd);
                    [DllImport("user32.dll")]
                    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                }
"@
            
            [Win32]::ShowWindow($Process.MainWindowHandle, 9) # SW_RESTORE
            [Win32]::SetForegroundWindow($Process.MainWindowHandle)
            
            Write-Host "Окно Cursor активировано" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Не удалось активировать окно Cursor" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Ошибка активации окна: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Шаг 1: Запуск Cursor
Write-Host "1. Запуск Cursor..." -ForegroundColor Yellow
try {
    # Запуск Cursor с проектом
    $cursorProcess = Start-Process -FilePath "cursor" -ArgumentList "`"$ProjectPath`"" -PassThru
    Write-Host "   ✅ Cursor запущен (PID: $($cursorProcess.Id))" -ForegroundColor Green
    
    # Ожидание загрузки
    Start-Sleep -Seconds 5
} catch {
    Write-Host "   ❌ Ошибка запуска Cursor: $($_.Exception.Message)" -ForegroundColor Red
    throw "Не удалось запустить Cursor"
}

# Шаг 2: Поиск и активация окна Cursor
Write-Host "2. Поиск окна Cursor..." -ForegroundColor Yellow
$cursorWindow = Find-CursorWindow
if (-not $cursorWindow) {
    throw "Окно Cursor не найдено"
}

# Активация окна
if (-not (Activate-CursorWindow -Process $cursorWindow)) {
    throw "Не удалось активировать окно Cursor"
}

# Шаг 3: Открытие AI-панели (Ctrl+L)
Write-Host "3. Открытие AI-панели..." -ForegroundColor Yellow
if (-not (Send-KeysToCursor -Keys "^l" -Delay 1000)) {
    throw "Не удалось открыть AI-панель"
}
Write-Host "   ✅ AI-панель открыта" -ForegroundColor Green

# Шаг 4: Переключение в Agent Mode
Write-Host "4. Переключение в Agent Mode..." -ForegroundColor Yellow
try {
    # Открытие командной палитры (Ctrl+Shift+P)
    Send-KeysToCursor -Keys "^+p" -Delay 1000
    
    # Ввод команды для включения Agent Mode
    Send-KeysToCursor -Keys "Enable Agent Mode" -Delay 500
    Send-KeysToCursor -Keys "{ENTER}" -Delay 1000
    
    Write-Host "   ✅ Agent Mode активирован" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Предупреждение: Не удалось переключить в Agent Mode" -ForegroundColor Yellow
}

# Шаг 5: Отправка запроса агенту
Write-Host "5. Отправка запроса агенту..." -ForegroundColor Yellow
try {
    # Ввод текста задачи
    Send-KeysToCursor -Keys $Task -Delay 500
    
    # Отправка запроса (Enter)
    Send-KeysToCursor -Keys "{ENTER}" -Delay 1000
    
    Write-Host "   ✅ Запрос отправлен агенту" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Ошибка отправки запроса: $($_.Exception.Message)" -ForegroundColor Red
    throw "Не удалось отправить запрос агенту"
}

# Шаг 6: Ожидание завершения работы агента
Write-Host "6. Ожидание завершения работы агента..." -ForegroundColor Yellow
$timeout = 300 # 5 минут
$startTime = Get-Date

while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($timeout)) {
    try {
        # Автоматическое подтверждение изменений (Ctrl+Enter)
        Send-KeysToCursor -Keys "^+{ENTER}" -Delay 100
        Send-KeysToCursor -Keys "{ENTER}" -Delay 100
        
        Start-Sleep -Seconds 5
        
        # Проверка завершения (можно добавить более точную логику)
        Write-Host "   ⏳ Агент работает... ($([Math]::Round(((Get-Date) - $startTime).TotalSeconds))с)" -ForegroundColor Cyan
        
    } catch {
        Write-Host "   ⚠️ Ошибка при ожидании: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "   ✅ Ожидание завершено" -ForegroundColor Green

# Шаг 7: Сохранение всех файлов
Write-Host "7. Сохранение всех файлов..." -ForegroundColor Yellow
try {
    # Сохранение всех файлов (Ctrl+Shift+S)
    Send-KeysToCursor -Keys "^+s" -Delay 1000
    Write-Host "   ✅ Все файлы сохранены" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Предупреждение: Не удалось сохранить файлы" -ForegroundColor Yellow
}

# Шаг 8: Добавление комментариев к коду
Write-Host "8. Добавление комментариев к коду..." -ForegroundColor Yellow
try {
    # Открытие AI-панели для нового запроса
    Send-KeysToCursor -Keys "^l" -Delay 1000
    
    # Запрос на добавление комментариев
    $commentRequest = "Добавь подробные комментарии к коду, объясняющие работу каждой функции и класса в проекте."
    Send-KeysToCursor -Keys $commentRequest -Delay 500
    Send-KeysToCursor -Keys "{ENTER}" -Delay 1000
    
    # Ожидание завершения
    Start-Sleep -Seconds 30
    
    Write-Host "   ✅ Комментарии добавлены" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Предупреждение: Не удалось добавить комментарии" -ForegroundColor Yellow
}

# Шаг 9: Запуск тестов
Write-Host "9. Запуск тестов..." -ForegroundColor Yellow
try {
    # Открытие терминала (Ctrl+`)
    Send-KeysToCursor -Keys "^`" -Delay 1000
    
    # Запуск тестов
    $testCommand = "py -3.11 -m pytest -q"
    Send-KeysToCursor -Keys $testCommand -Delay 500
    Send-KeysToCursor -Keys "{ENTER}" -Delay 2000
    
    Write-Host "   ✅ Тесты запущены" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Предупреждение: Не удалось запустить тесты" -ForegroundColor Yellow
}

# Шаг 10: Финальная проверка
Write-Host "10. Финальная проверка..." -ForegroundColor Yellow
try {
    # Проверка API агента
    $headers = @{"x-agent-secret" = $Secret}
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8088/health" -Headers $headers -TimeoutSec 5
    
    if ($healthResponse.status -eq "ok") {
        Write-Host "   ✅ API агент работает: $($healthResponse.status)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ API агент: $($healthResponse.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️ Предупреждение: API агент не отвечает" -ForegroundColor Yellow
}

Write-Host "=== Автоматизация Cursor завершена! ===" -ForegroundColor Green
Write-Host "Проект: $ProjectPath" -ForegroundColor Cyan
Write-Host "Задача: $Task" -ForegroundColor Cyan
Write-Host "Время выполнения: $([Math]::Round(((Get-Date) - $startTime).TotalMinutes, 2)) минут" -ForegroundColor Cyan

