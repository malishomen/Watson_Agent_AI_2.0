# 🧠 Watson Agent + Cursor Automation  
**Полный автозапуск и эксплуатация системы**

---

## 📂 Компоненты проекта
- `cursor_automation_fixed.ps1` — полный PowerShell оркестратор  
- `start_cursor_automation_fixed.ps1` — драйвер с Python (`pyautogui`)  
- `WatsonAgent.bat` / `WatsonAgent_Advanced.bat` / `WatsonAgent_Stop.bat` — управление агентом  
- `start_windows_autorun.bat` — автозапуск при старте Windows  
- `logs/` — логи работы агента и автоматизации  

---

## ⚡ Ключевые патчи
1. **UTF-8 Anti-Cyrillic Header** — защита от паразитной «с»  
2. **EN Keyboard Layout** — принудительная английская раскладка  
3. **Safe Task Passing** — задачи передаются через JSON  
4. **Robust Cursor Detection** — поиск `cursor.exe` по стандартным путям  
5. **Terminal via Palette** — открытие терминала через палитру  
6. **Enhanced Auto-Confirm** — надёжное подтверждение изменений  
7. **UTF-8 Logging** — корректные логи  

---

## ⚙️ Подготовка среды
1. Установить **PowerShell 7 (pwsh)**  
2. Установить **Python 3.11+** + зависимости:
   ```powershell
   py -3.11 -m pip install pyautogui pillow
   ```
3. Установить **Docker Desktop** и включить автозапуск  
4. Установить **LM Studio**, включить `Developer → Local Server`  
5. В Cursor включить **Agent Mode** и опцию **Install Shell Command: cursor**  

---

## ▶️ Ручной запуск

### A) Полный оркестратор
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\cursor_automation_fixed.ps1 `
  -ProjectPath "D:\AI-Agent" `
  -Task "Создай REST API на FastAPI с PostgreSQL и тестами" `
  -Timeout 900
```

### B) Драйвер с Python
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\start_cursor_automation_fixed.ps1 `
  -ProjectPath "D:\AI-Agent" `
  -Task "Create simple test application" `
  -Timeout 300
```

---

## 🔄 Автоматический запуск при старте Windows

### 1. Создаём батник `D:\AI-Agent\start_windows_autorun.bat`
```bat
@echo off
chcp 65001 >nul

REM === Запуск Docker Desktop ===
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

REM === Запуск LM Studio ===
start "" "C:\Program Files\LM Studio\LM Studio.exe"

REM Ждём 15 секунд для загрузки сервисов
timeout /t 15 /nobreak >nul

REM === Запуск WatsonAgent API + Telegram Bot ===
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AI-Agent\WatsonAgent.bat"

REM === Запуск Cursor с автоматизацией ===
pwsh -NoProfile -ExecutionPolicy Bypass -File "D:\AI-Agent\start_cursor_automation_fixed.ps1" -Task "Init system startup run" -Timeout 120
```

### 2. Добавляем в автозагрузку
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WatsonAgent.lnk")
$Shortcut.TargetPath = "D:\AI-Agent\start_windows_autorun.bat"
$Shortcut.Save()
```

---

## 📊 Проверка после перезагрузки
1. Windows стартует → автоматически поднимается Docker и LM Studio  
2. Через ~15 сек запускается WatsonAgent API и бот  
3. Стартует Cursor и агент выполняет тестовую задачу  
4. Логи сохраняются в `D:\AI-Agent\logs\`  
5. Проверка доступности:
   ```powershell
   curl http://127.0.0.1:8088/health
   ```

---

## 📈 Архитектура системы
![Watson Agent Architecture](watson_agent_architecture.png)

---

## 🧭 Итог
- ✅ Полный автозапуск вместе с Windows  
- ✅ Docker, LM Studio, WatsonAgent, Cursor запускаются сами  
- ✅ Автоматическая проверка и тестовая задача при старте  
- ✅ Возможность ручного запуска оркестратора или драйвера  
