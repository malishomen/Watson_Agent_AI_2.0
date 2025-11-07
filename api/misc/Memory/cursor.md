# 🚀 AI-Agent + Cursor Integration Guide

## 1. Подготовка API

Убедись, что API агента запущен:

```powershell
cd D:\AI-Agent
$env:AGENT_HTTP_SHARED_SECRET = "ТВОЙ_СЕКРЕТ"
uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info
```

Проверка:

```powershell
irm http://127.0.0.1:8088/health
```

---

## 2. Переменные окружения (для Cursor)

В `settings.json` Cursor или в PowerShell укажи:

```powershell
$env:AGENT_API_BASE = "http://127.0.0.1:8088"
$env:AGENT_HTTP_SHARED_SECRET = "ТВОЙ_СЕКРЕТ"
```

---

## 3. Доступные эндпоинты

### 🟢 Проверка здоровья

```
GET /health
Headers: { x-agent-secret: <секрет> }
```

### 💬 Команды

```
POST /command
Body:
{
  "text": "запусти notepad",
  "session": "TG-Danil"
}
```

### 📂 Файлы

* `/read D:\file.txt` → читает файл
* `/write D:\file.txt ::: текст` → пишет в файл

### ⚡ Проекты

* `POST /project/validate`
* `POST /project/run`
* `GET /project/status?project_id=demo`

---

## 4. Примеры запросов из Cursor (tasks.code.json)

```json
{
  "label": "AI-Agent Command",
  "url": "{{AGENT_API_BASE}}/command",
  "method": "POST",
  "headers": {
    "x-agent-secret": "{{AGENT_HTTP_SHARED_SECRET}}"
  },
  "body": {
    "text": "{{input}}",
    "session": "Cursor"
  }
}
```

```json
{
  "label": "AI-Agent Project Run",
  "url": "{{AGENT_API_BASE}}/project/run",
  "method": "POST",
  "headers": {
    "x-agent-secret": "{{AGENT_HTTP_SHARED_SECRET}}"
  },
  "body": {
    "project_id": "{{input}}",
    "resume": true
  }
}
```

---

## 5. Тестовые команды (через Cursor Prompt)

* **`где я`** → вернёт текущую директорию
* **`запусти notepad`** → откроет блокнот
* **`прочитай D:\AI-Agent\README.md`** → вернёт содержимое файла
* **`запусти проект demo`** → запустит демо проект

---

## 6. Безопасность

* Все операции идут через **секретный ключ** (`x-agent-secret`)
* Опасные действия (удаление, системные процессы) требуют `/approve <ID>`
* Белые списки директорий: `D:\AI-Agent`, `D:\Projects`, `D:\Temp`

---

## ✅ Итог

Теперь Cursor сможет напрямую дергать наш API:

* Ты пишешь **естественный текст** → NLP парсер превращает его в команду
* Агент выполняет → результат возвращается в Cursor или Telegram

---

## 📝 Дополнительные настройки

### Настройка Cursor для работы с AI-Agent

1. **Открой настройки Cursor** (`Ctrl + ,`)
2. **Добавь переменные окружения** в секцию Environment Variables:
   ```json
   {
     "AGENT_API_BASE": "http://127.0.0.1:8088",
     "AGENT_HTTP_SHARED_SECRET": "ТВОЙ_СЕКРЕТ"
   }
   ```

3. **Создай файл tasks.code.json** в корне проекта:
   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "AI-Agent Command",
         "type": "shell",
         "command": "curl",
         "args": [
           "-X", "POST",
           "http://127.0.0.1:8088/command",
           "-H", "x-agent-secret: ${env:AGENT_HTTP_SHARED_SECRET}",
           "-H", "Content-Type: application/json",
           "-d", "{\"text\": \"${input}\", \"session\": \"Cursor\"}"
         ],
         "group": "build",
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

### Автоматизация запуска

Создай PowerShell скрипт `start-agent.ps1`:

```powershell
# start-agent.ps1
$env:AGENT_HTTP_SHARED_SECRET = "ТВОЙ_СЕКРЕТ"
cd D:\AI-Agent
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn api.fastapi_agent_fixed:app --host 127.0.0.1 --port 8088 --http h11 --loop asyncio --workers 1 --no-access-log --log-level info"
```

Запуск: `.\start-agent.ps1`

---

## 🔧 Устранение неполадок

### API не отвечает
```powershell
# Проверь, что процесс запущен
netstat -an | findstr :8088

# Перезапусти API
taskkill /f /im python.exe
# затем запусти заново
```

### Ошибки аутентификации
- Проверь, что `AGENT_HTTP_SHARED_SECRET` совпадает в API и Cursor
- Убедись, что заголовок `x-agent-secret` передается корректно

### Проблемы с путями
- Убедись, что все пути используют правильные разделители (`\` для Windows)
- Проверь права доступа к целевым директориям

