# 🚀 AI-Agent × Cursor — Боевой Чек-лист

## ⚡ Быстрый запуск (3 шага)

### 1. Настройка секрета
Открой `D:\AI-Agent` в Cursor → проверь секрет в `.vscode\settings.json`

```json
{
  "terminal.integrated.env.windows": {
    "AGENT_API_BASE": "http://127.0.0.1:8088",
    "AGENT_HTTP_SHARED_SECRET": "REPLACE_WITH_YOUR_SECRET"
  }
}
```

### 2. Запуск API
`Ctrl+Shift+P` → **Tasks: Run Task** → **AA: Start API**
*(внизу появится uvicorn-лог; это и есть наш API)*

### 3. Проверка здоровья
`Ctrl+Shift+P` → **AA: Health Check**
*ожидаем ответ: `{"status":"ok"}`*

---

## 🎯 Быстрые команды (через задание в Cursor)

### **AA: Command (prompt)** → вводи текст:

* `где я` → покажет WORKDIR
* `запусти notepad` → /run "notepad"
* `прочитай D:\AI-Agent\README.md` → /read …
* `запусти проект demo` → /project.run demo
* `статус проекта demo` → /project.status demo

---

## 📦 Проекты "под ключ"

* **AA: Project Validate (prompt path)** → укажи путь к `ProjectSpec.yml`
* **AA: Project Run (prompt id)** → введи `demo`
* **AA: Project Status (prompt id)** → введи `demo`
* **AA: Approvals Pending** → список заявок; подтверждать: `/approve AP-XXXX` через **AA: Command (prompt)**

## 🔥 Создание проекта с нуля

* **AA: Scaffold FastAPI+Postgres** → создает полный проект:
  - FastAPI приложение
  - PostgreSQL база данных
  - Docker Compose
  - Готовые API endpoints
  - ProjectSpec.yml для AI-Agent
  - Автоматическая документация

---

## 🔥 Горячие клавиши

| Клавиши | Действие |
|---------|----------|
| `Ctrl+Shift+P` | Открыть палитру команд |
| `Ctrl+Shift+P` → `Tasks: Run Task` | Список задач |
| `Ctrl+Shift+P` → `AA: Start API` | Запуск API агента |
| `Ctrl+Shift+P` → `AA: Health Check` | Проверка здоровья |
| `Ctrl+Shift+P` → `AA: Command (prompt)` | Выполнение команд |

---

## 🛠️ Если что-то не так (шпаргалка)

### **401 Unauthorized:**
В Cursor → `.vscode\settings.json` и **AA: Start API** должны использовать **один и тот же** секрет.
Проверь:
```powershell
irm $env:AGENT_API_BASE/health -Headers @{ 'x-agent-secret' = $env:AGENT_HTTP_SHARED_SECRET }
```

### **`ModuleNotFoundError: No module named 'api'`:**
API запускай из `D:\AI-Agent` (задача **AA: Start API** уже делает `cd`).

### **Порт занят/не отвечает:**
```powershell
Get-Process | ? {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force
```
потом снова **AA: Start API**.

### **Русский текст "ломается":**
Везде запускаем PowerShell c `-NoProfile` и `charset=utf-8` (так уже настроено в задачах).

### **Файл-загрузка не работает:**
Установи зависимость (один раз):
```powershell
pip install python-multipart
```

---

## 📱 Телеграм (краткий пуск)

Если решишь подключить чат-управление сейчас:

```powershell
$env:TG_BOT_TOKEN="тут_твой_токен"
python telegram_bot.py
```

Пиши боту: `где я`, `запусти проект demo`, `статус проекта demo`.

---

## 🎯 Готовые задачи в Cursor

1. **AA: Start API** - запуск API агента
2. **AA: Health Check** - проверка здоровья
3. **AA: Command (prompt)** - выполнение команд
4. **AA: Project Validate (prompt path)** - валидация проекта
5. **AA: Project Run (prompt id)** - запуск проекта
6. **AA: Project Status (prompt id)** - статус проекта
7. **AA: Approvals Pending** - список заявок
8. **AA: Scaffold FastAPI+Postgres** - создание проекта с нуля 🔥

---

## ✅ Чек-лист готовности

- [ ] Cursor открыт в `D:\AI-Agent`
- [ ] Секрет настроен в `.vscode\settings.json`
- [ ] `python-multipart` установлен
- [ ] **AA: Start API** выполнен успешно
- [ ] **AA: Health Check** возвращает `{"status":"ok"}`
- [ ] **AA: Command (prompt)** работает с командой `где я`

**Готово к бою!** 🚀
