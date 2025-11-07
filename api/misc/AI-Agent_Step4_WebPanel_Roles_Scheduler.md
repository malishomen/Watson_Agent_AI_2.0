# AI-Agent Step 4: Веб-панель + Роли + Планировщик

> **Цель**: Создать полноценную веб-панель оператора с ролевой системой и планировщиком задач
> **Технологии**: FastAPI + Jinja2 + HTMX + SQLite + APScheduler
> **Результат**: Готовая к работе система управления агентом через веб-интерфейс

---

## 1) Архитектура Step 4

### 1.1 Структура проекта
```
D:\AI-Agent\
├── ui/                          # Веб-панель
│   ├── __init__.py
│   ├── main.py                  # FastAPI приложение с UI
│   ├── auth.py                  # Аутентификация и роли
│   ├── templates/               # Jinja2 шаблоны
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── logs.html
│   │   ├── specs.html
│   │   ├── approvals.html
│   │   └── scheduler.html
│   └── static/                  # CSS, JS, HTMX
│       ├── style.css
│       ├── app.js
│       └── htmx.min.js
├── scheduler/                   # Планировщик
│   ├── __init__.py
│   ├── core.py                  # APScheduler интеграция
│   ├── models.py                # Модели расписаний
│   └── notifications.py         # Telegram уведомления
├── roles/                       # Ролевая система
│   ├── __init__.py
│   ├── auth.py                  # Проверка прав
│   └── permissions.py           # Матрица разрешений
└── migrations/                  # Миграции БД
    ├── __init__.py
    └── 001_add_ui_tables.sql
```

### 1.2 Роли и права
- **readonly**: Просмотр логов, статуса, ProjectSpec
- **operator**: + Запуск проектов, подтверждение операций
- **admin**: + Управление пользователями, планировщик, настройки

---

## 2) Веб-панель оператора

### 2.1 Основные страницы

#### `/ui/dashboard` - Главная панель
- Статус агента (онлайн/оффлайн)
- Последние операции из `ops_log.csv`
- Активные проекты
- Очередь подтверждений

#### `/ui/logs` - Лента операций
- Фильтрация по дате, типу операции, статусу
- Поиск по содержимому
- Экспорт в CSV
- Real-time обновления через HTMX

#### `/ui/specs` - Управление ProjectSpec
- Список всех `.yml` файлов
- Редактор с подсветкой синтаксиса
- Предварительный просмотр
- История изменений

#### `/ui/approvals` - Подтверждения
- Список ожидающих подтверждения операций
- Кнопки "Approve" / "Reject"
- Детали операции (путь, параметры)
- История решений

#### `/ui/scheduler` - Планировщик
- Список запланированных задач
- CRUD операции с расписаниями
- Статусы выполнения
- Логи планировщика

### 2.2 Технические детали

#### FastAPI + Jinja2 интеграция
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI-Agent Web Panel")
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")

@app.get("/ui/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_role: str = Depends(get_current_user_role)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "role": user_role})
```

#### HTMX для real-time обновлений
```html
<!-- Обновление логов каждые 5 секунд -->
<div hx-get="/ui/api/logs/recent" hx-trigger="every 5s" hx-swap="innerHTML">
    <!-- Логи загружаются здесь -->
</div>

<!-- Кнопка подтверждения -->
<button hx-post="/ui/api/approve/AP-123456" 
        hx-confirm="Подтвердить операцию?" 
        hx-target="#approval-status">
    Подтвердить
</button>
```

---

## 3) Ролевая система

### 3.1 Аутентификация
```python
# Простая аутентификация через shared secret + роль
class User:
    def __init__(self, role: str, permissions: List[str]):
        self.role = role
        self.permissions = permissions

# Роли по умолчанию
ROLES = {
    "readonly": ["view_logs", "view_specs", "view_status"],
    "operator": ["view_logs", "view_specs", "view_status", "run_projects", "approve_ops"],
    "admin": ["*"]  # Все права
}
```

### 3.2 Проверка прав на эндпоинтах
```python
def require_permission(permission: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = get_current_user()
            if permission not in user.permissions and "*" not in user.permissions:
                raise HTTPException(403, "Недостаточно прав")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/ui/api/run-project")
@require_permission("run_projects")
async def run_project(spec_path: str):
    # Запуск проекта
    pass
```

---

## 4) Планировщик задач

### 4.1 APScheduler интеграция
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

# Запуск ProjectSpec по расписанию
@scheduler.scheduled_job('cron', hour=9, minute=0)  # Каждый день в 9:00
async def daily_backup():
    await run_project_spec("D:/AI-Agent/specs/daily_backup.yml")

# Периодическая проверка статуса
@scheduler.scheduled_job('interval', minutes=5)
async def health_check():
    status = await check_agent_health()
    if not status:
        await send_telegram_alert("Агент недоступен!")
```

### 4.2 Модели расписаний
```python
class ScheduleTask:
    id: str
    name: str
    spec_path: str
    trigger_type: str  # cron, interval, date
    trigger_config: dict
    enabled: bool
    last_run: datetime
    next_run: datetime
    created_at: datetime
```

### 4.3 Telegram уведомления
```python
async def send_notification(message: str, level: str = "info"):
    """Отправка уведомления в Telegram"""
    if level == "error":
        await send_to_admin_chat(f"🚨 ОШИБКА: {message}")
    elif level == "success":
        await send_to_admin_chat(f"✅ УСПЕХ: {message}")
    else:
        await send_to_admin_chat(f"ℹ️ ИНФО: {message}")
```

---

## 5) Готовые файлы для реализации

### 5.1 Основные компоненты
- `ui/main.py` - FastAPI приложение с маршрутами
- `ui/templates/base.html` - Базовый шаблон с Bootstrap
- `ui/templates/dashboard.html` - Главная панель
- `scheduler/core.py` - Планировщик задач
- `roles/auth.py` - Аутентификация и авторизация

### 5.2 Cursor tasks
```json
{
  "title": "Step 4: Install UI dependencies",
  "description": "Установка зависимостей для веб-панели",
  "steps": [
    { "type": "terminal", "command": "pip install jinja2 python-multipart apscheduler" },
    { "type": "terminal", "command": "pip install python-dotenv" }
  ]
},
{
  "title": "Step 4: Start web panel",
  "description": "Запуск веб-панели оператора",
  "steps": [
    { "type": "terminal", "command": "uvicorn ui.main:app --host 127.0.0.1 --port 8080 --reload" }
  ]
},
{
  "title": "Step 4: Test web panel",
  "description": "Тестирование веб-панели",
  "steps": [
    { "type": "terminal", "command": "curl http://127.0.0.1:8080/ui/dashboard" },
    { "type": "note", "content": "Откройте http://127.0.0.1:8080/ui/dashboard в браузере" }
  ]
}
```

---

## 6) Пошаговый план реализации

### Этап 1: Базовая веб-панель (2-3 часа)
1. Создать FastAPI приложение с Jinja2
2. Добавить базовые шаблоны и стили
3. Реализовать dashboard с логами
4. Добавить HTMX для real-time обновлений

### Этап 2: Управление ProjectSpec (1-2 часа)
1. Создать редактор YAML файлов
2. Добавить предварительный просмотр
3. Реализовать запуск проектов через UI
4. Добавить историю изменений

### Этап 3: Система подтверждений (1 час)
1. Создать страницу approvals
2. Реализовать кнопки подтверждения
3. Добавить детали операций
4. Интегрировать с существующей системой

### Этап 4: Ролевая система (1-2 часа)
1. Создать простую аутентификацию
2. Реализовать проверку прав
3. Добавить декораторы для эндпоинтов
4. Создать матрицу разрешений

### Этап 5: Планировщик (2-3 часа)
1. Интегрировать APScheduler
2. Создать UI для управления расписаниями
3. Добавить Telegram уведомления
4. Реализовать мониторинг выполнения

---

## 7) Готовые команды для запуска

### Быстрый старт
```powershell
# 1. Установка зависимостей
pip install jinja2 python-multipart apscheduler python-dotenv

# 2. Запуск веб-панели
uvicorn ui.main:app --host 127.0.0.1 --port 8080 --reload

# 3. Открытие в браузере
Start-Process "http://127.0.0.1:8080/ui/dashboard"
```

### Тестирование
```powershell
# Проверка API
curl http://127.0.0.1:8080/ui/api/status

# Проверка логов
curl http://127.0.0.1:8080/ui/api/logs/recent

# Проверка ProjectSpec
curl http://127.0.0.1:8080/ui/api/specs/list
```

---

## 8) Ожидаемый результат

После реализации Step 4 у вас будет:

✅ **Веб-панель оператора** - полноценный UI для управления агентом
✅ **Ролевая система** - контроль доступа для разных пользователей  
✅ **Планировщик задач** - автоматическое выполнение проектов по расписанию
✅ **Real-time мониторинг** - live обновления статуса и логов
✅ **Telegram интеграция** - уведомления о событиях
✅ **Безопасность** - маскирование чувствительных данных

**Готов к реализации? Скажите "Поехали" - упакую все файлы и tasks для Cursor!**
