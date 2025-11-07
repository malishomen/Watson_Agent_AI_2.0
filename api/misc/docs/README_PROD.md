# 🚀 AI-Agent Production Pack

**Полный гайд по боевому использованию AI-Agent системы**

---

## 📦 Быстрый старт (One-Click Install)

### 🎯 Установка в один клик
```powershell
# Перейти в папку проекта
cd D:\AI-Agent

# Запустить батон-установщик
.\scripts\install_agent.ps1
```

**Что делает батон:**
- ✅ Очищает старые процессы
- ✅ Настраивает UTF-8 кодировку
- ✅ Активирует виртуальное окружение
- ✅ Обновляет пакеты
- ✅ Генерирует секрет API
- ✅ Создает бэкап
- ✅ Запускает API
- ✅ Настраивает автозапуск
- ✅ Запускает watchdog
- ✅ Проводит тестовую команду

---

## 🔧 Карманный набор команд

### Статус системы
```powershell
# Проверка здоровья API
irm http://127.0.0.1:8088/health

# Быстрая диагностика
.\scripts\incident_playbook.ps1 -Action status
```

### Выполнение команд
```powershell
# Настройка переменных
$h = @{ 'x-agent-secret' = $env:AGENT_HTTP_SHARED_SECRET }

# Выполнить команду
$body = @{ text = 'где я'; session = 'cron' } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# Русские команды
$body = @{ text = 'запусти notepad'; session = 'Telegram' } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

### Pending approvals
```powershell
# Список ожидающих подтверждения
$h = @{ 'x-agent-secret' = $env:AGENT_HTTP_SHARED_SECRET }
irm -Method Get http://127.0.0.1:8088/approvals/pending -Headers $h

# Подтвердить заявку
$body = @{ text = '/approve AP-1234567890'; session = 'admin' } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

---

## 🤖 Telegram интеграция

### Базовый хук для бота
```python
import os, requests

API = "http://127.0.0.1:8088/command"
SECRET = os.getenv("AGENT_HTTP_SHARED_SECRET", "")

def send_to_agent(text, session="Telegram"):
    """Отправляет команду агенту"""
    try:
        r = requests.post(API,
            json={"text": text, "session": session},
            headers={
                "x-agent-secret": SECRET, 
                "Content-Type": "application/json; charset=utf-8"
            },
            timeout=20)
        j = r.json()
        if j.get("ok"):
            return f"→ {j.get('normalized', '')}\n\n{j.get('result', '')}"
        else:
            return f"❌ Ошибка: {j.get('result', 'Unknown error')}"
    except Exception as e:
        return f"❌ Ошибка соединения: {e}"

# Использование
result = send_to_agent("где я")
print(result)
```

### Мониторинг pending approvals
```python
import os, time, requests

API = "http://127.0.0.1:8088/approvals/pending"
HDR = {"x-agent-secret": os.getenv("AGENT_HTTP_SHARED_SECRET", "")}

def poll_pending_approvals(send_message_func):
    """Мониторинг ожидающих подтверждения заявок"""
    while True:
        try:
            items = requests.get(API, headers=HDR, timeout=10).json()
            for item in items:
                msg = f"""⏳ Ждёт подтверждения:
🆔 ID: {item['id']}
📝 Действие: {item['action']}
📋 Параметры: {item['params']}
⏰ Создано: {item['created_at']}

✅ Ответь: /approve {item['id']}"""
                send_message_func(msg)
        except Exception as e:
            send_message_func(f"⚠️ Ошибка мониторинга: {e}")
        time.sleep(30)  # Проверка каждые 30 секунд
```

### Полная интеграция с Telegram Bot
```python
import os, requests, time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Настройки
API_URL = "http://127.0.0.1:8088/command"
SECRET = os.getenv("AGENT_HTTP_SHARED_SECRET", "")

class AIAgentBot:
    def __init__(self, token):
        self.app = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("pending", self.pending))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context):
        await update.message.reply_text("🤖 AI-Agent Bot готов к работе!\n\nКоманды:\n/status - статус системы\n/pending - ожидающие подтверждения\n\nИли просто напишите команду на русском/английском!")
    
    async def status(self, update: Update, context):
        try:
            health = requests.get("http://127.0.0.1:8088/health", timeout=5)
            await update.message.reply_text(f"✅ API: {health.json()['status']}")
        except:
            await update.message.reply_text("❌ API недоступен")
    
    async def pending(self, update: Update, context):
        try:
            h = {"x-agent-secret": SECRET}
            items = requests.get("http://127.0.0.1:8088/approvals/pending", headers=h, timeout=5).json()
            if items:
                msg = f"⏳ Ожидают подтверждения ({len(items)} заявок):\n\n"
                for item in items[:3]:  # Показываем первые 3
                    msg += f"🆔 {item['id']}\n📝 {item['action']}\n✅ /approve {item['id']}\n\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text("✅ Нет ожидающих подтверждения заявок")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def handle_message(self, update: Update, context):
        text = update.message.text
        try:
            result = self.send_to_agent(text, f"TG-{update.effective_user.id}")
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    def send_to_agent(self, text, session="Telegram"):
        """Отправляет команду агенту"""
        try:
            r = requests.post(API_URL,
                json={"text": text, "session": session},
                headers={
                    "x-agent-secret": SECRET,
                    "Content-Type": "application/json; charset=utf-8"
                },
                timeout=20)
            j = r.json()
            if j.get("ok"):
                return f"→ {j.get('normalized', '')}\n\n{j.get('result', '')}"
            else:
                return f"❌ Ошибка: {j.get('result', 'Unknown error')}"
        except Exception as e:
            return f"❌ Ошибка соединения: {e}"

# Запуск бота
if __name__ == "__main__":
    bot = AIAgentBot("YOUR_BOT_TOKEN")
    bot.app.run_polling()
```

---

## 🔧 Ежедневное управление

### Проверка здоровья системы
```powershell
# Полная проверка с подробностями
.\scripts\daily_health_check.ps1 -Verbose

# Быстрая проверка
.\scripts\incident_playbook.ps1 -Action status
```

### Управление процессами
```powershell
# Диагностика проблем
.\scripts\incident_playbook.ps1 -Action diagnose

# Перезапуск системы
.\scripts\incident_playbook.ps1 -Action restart

# Полный сброс
.\scripts\incident_playbook.ps1 -Action full-reset
```

### Бэкапы
```powershell
# Создать бэкап
.\scripts\backup_min.ps1

# Бэкап с очисткой старых
.\scripts\backup_min.ps1 -CleanOld
```

---

## 🚨 Инцидент-плейбук

### Если API не отвечает
```powershell
# 1. Диагностика
.\scripts\incident_playbook.ps1 -Action diagnose

# 2. Перезапуск
.\scripts\incident_playbook.ps1 -Action restart

# 3. Если не помогло - полный сброс
.\scripts\incident_playbook.ps1 -Action full-reset
```

### Если зависает
```powershell
# Остановить все процессы
Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" } | Stop-Process -Force

# Запустить заново
.\scripts\install_agent.ps1 -SkipBackup
```

### Если проблемы с кодировкой
```powershell
# Сброс кодировки
chcp 65001
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Перезапуск
.\scripts\incident_playbook.ps1 -Action restart
```

---

## 📊 Мониторинг и логи

### Логи операций
```powershell
# Последние операции
Get-Content D:\AI-Agent\Memory\ops_log.csv | Select-Object -Last 10

# Поиск ошибок
Get-Content D:\AI-Agent\Memory\ops_log.csv | Where-Object { $_ -match "FAIL" }

# Статистика за день
Get-Content D:\AI-Agent\Memory\ops_log.csv | Where-Object { $_ -match (Get-Date -Format "yyyy-MM-dd") }
```

### Мониторинг процессов
```powershell
# Процессы Python/Uvicorn
Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }

# Порт 8088
netstat -ano | findstr ":8088"

# Использование памяти
Get-Process | Where-Object { $_.ProcessName -match "python" } | Select-Object ProcessName, WorkingSet
```

---

## 🔒 Безопасность

### Проверка секрета
```powershell
# Длина секрета (должна быть >= 32)
$env:AGENT_HTTP_SHARED_SECRET.Length

# Проверка на пробелы (не должно быть)
$env:AGENT_HTTP_SHARED_SECRET -match ' '
```

### Белые списки
- ✅ `D:\AI-Agent` - основная папка
- ✅ `D:\Projects` - проекты
- ✅ `D:\Temp` - временные файлы
- ❌ `System32` - исключен из белого списка

### Approvals система
- ✅ Все destructive операции требуют `/approve`
- ✅ Approvals персистентные в SQLite
- ✅ Все операции логируются в `ops_log.csv`

---

## 🎯 Готовые команды для тестирования

### Базовые команды
```powershell
# Где я
$body = @{ text = 'где я' } | ConvertTo-Json -Compress

# Запуск программы
$body = @{ text = 'запусти notepad' } | ConvertTo-Json -Compress

# Список процессов
$body = @{ text = 'покажи процессы' } | ConvertTo-Json -Compress

# Чтение файла
$body = @{ text = '/read D:\AI-Agent\README.md' } | ConvertTo-Json -Compress
```

### Команды с approvals
```powershell
# Запись в файл (требует подтверждения)
$body = @{ text = 'запиши в D:\test.txt: Привет из Telegram' } | ConvertTo-Json -Compress

# После получения AP-... ID:
$body = @{ text = '/approve AP-1234567890' } | ConvertTo-Json -Compress
```

---

## 📋 Чек-лист готовности к продакшену

- [x] ✅ API запущен и отвечает на `/health`
- [x] ✅ Команды выполняются через `/command`
- [x] ✅ Кириллица работает корректно
- [x] ✅ Approvals система функционирует
- [x] ✅ Автозапуск настроен
- [x] ✅ Watchdog запущен
- [x] ✅ Бэкапы настроены
- [x] ✅ Логирование работает
- [x] ✅ Безопасность проверена
- [x] ✅ Telegram интеграция готова

---

## 🚀 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!

**Все компоненты протестированы и готовы к боевому использованию.**

**Для быстрого старта:**
```powershell
cd D:\AI-Agent
.\scripts\install_agent.ps1
```

**Для ежедневного использования:**
```powershell
.\scripts\daily_health_check.ps1 -Verbose
```

**Для решения проблем:**
```powershell
.\scripts\incident_playbook.ps1 -Action diagnose
```

---

*Создано: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*
*Версия: Production Pack v1.0*
