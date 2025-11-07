# Cursor — Аудит, харднинг и курс дальше (Step 2 ✔ → Step 3+)

> Мы — МОЗГ. Агент — РУКИ. Step 2 закрыт «под ключ» — фикс WORKDIR, ProjectSpec + Runner, безопасность, логи. Ниже — короткий аудит, безопасные правки, быстрые тесты и дорожная карта. Готово к запуску из Cursor.

---

## 1) Что уже сделано и работает (итог Step 2)
- **WORKDIR-персист** через SQLite `settings` (команда `/cd` сохраняет, `/pwd` проверяет).
- **ProjectSpec.yml** + **run_project.py** — исполнитель ТЗ.
- **Команды**: `/run`, `/read`, `/write`, `/kill`, `/cd`, `/pwd`, `/approve`.
- **Безопасность**: белый список директорий, approve вне whitelist.
- **Логи**: `D:\AI-Agent\Memory\ops_log.csv`.
- **Cursor-tasks**: подготовлены и проходят.

---

## 2) Харднинг безопасности (сделать сразу)

### 2.1. Очистить whitelist (убрать System32)
В `GPT+Deepseek_Agent_memory.py`:
```python
from pathlib import Path
WHITELIST_DIRS = [
    Path("D:\\AI-Agent").resolve(),
    Path("D:\\Projects").resolve(),
    Path("D:\\Temp").resolve(),
]
# никаких System32
```

### 2.2. Секреты НЕ храним в отчётах
- Пересоздайте токен бота в @BotFather и **не светите** его в коде/логах.
- Обновите `AGENT_HTTP_SHARED_SECRET` (32–64 символа).

Пример обновления (PowerShell):
```powershell
$env:AGENT_HTTP_SHARED_SECRET = "<LONG_RANDOM_64>"
setx AGENT_HTTP_SHARED_SECRET $env:AGENT_HTTP_SHARED_SECRET

$env:TELEGRAM_BOT_TOKEN = "<NEW_BOT_TOKEN>"
setx TELEGRAM_BOT_TOKEN $env:TELEGRAM_BOT_TOKEN
```

### 2.3. Telegram: approve — только админ
В `bot/telegram_operator.py` (фрагмент `/approve`):
```python
if str(uid) != str(ADMIN):
    await update.message.reply_text("Только админ может подтверждать.")
    return
```

### 2.4. API только с секретом
- Держим API на `127.0.0.1`.
- Все POST/GET требуют заголовок: `x-agent-secret: <секрет>`.

---

## 3) Быстрые контрольные тесты

### 3.1. API авторизация
```powershell
# Без секрета — ожидаем 401
powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/workdir' -Method GET | Select-Object -Expand StatusCode

# С секретом — видим stdout pwd
powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/workdir' -Headers @{ 'x-agent-secret'=$env:AGENT_HTTP_SHARED_SECRET } -Method GET | Select-Object -Expand Content
```

### 3.2. Telegram права
- Команда `/approve AP-...` от НЕ-админа → **отказ**.
- Та же команда от `TELEGRAM_ADMIN_USER_ID` → **проходит**.

### 3.3. ProjectSpec — полный прогон
```powershell
python run_project.py ProjectSpec.yml
```
Ожидаем запрос `/approve` на шаге вне `WHITELIST_DIRS` + запись в `ops_log.csv`.

---

## 4) Удобные улучшения (по желанию)

### 4.1. UTF‑8 в PowerShell
```powershell
chcp 65001
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
```

### 4.2. Бэкап и чистка БД (раз в неделю)
```sql
PRAGMA wal_checkpoint(TRUNCATE);
VACUUM;
```

### 4.3. Лог раннера
Добавьте дубли в `D:\AI-Agent\Memory\run_project.log` (дата, шаг, RC).

---

## 5) Cursor — готовые задачи (добавить/актуализировать в `cursor\tasks.code.json`)

```json
{
  "title": "Security: tighten whitelist + secrets",
  "description": "Ужесточение whitelist и ротация секретов",
  "steps": [
    { "type": "note", "content": "В коде агента очистить WHITELIST_DIRS: только D:\\AI-Agent, D:\\Projects, D:\\Temp" },
    { "type": "terminal", "command": "$env:AGENT_HTTP_SHARED_SECRET = \"<LONG_RANDOM_64>\"; setx AGENT_HTTP_SHARED_SECRET $env:AGENT_HTTP_SHARED_SECRET" },
    { "type": "note", "content": "Сгенерируйте новый TELEGRAM_BOT_TOKEN в @BotFather и задайте переменную окружения" }
  ]
},
{
  "title": "API: auth smoke test",
  "description": "Проверка 401/200 для API",
  "steps": [
    { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/workdir' -Method GET | Select-Object -Expand StatusCode" },
    { "type": "terminal", "command": "powershell Invoke-WebRequest -Uri 'http://127.0.0.1:8088/workdir' -Headers @{ 'x-agent-secret'=$env:AGENT_HTTP_SHARED_SECRET } -Method GET | Select-Object -Expand Content" }
  ]
},
{
  "title": "Project: run spec (full)",
  "description": "Полный прогон demo-спецификации",
  "steps": [
    { "type": "terminal", "command": "python run_project.py ProjectSpec.yml" },
    { "type": "terminal", "command": "python Memory/GPT+Deepseek_Agent_memory.py --session Danil-PC --once \"/read D:\\AI-Agent\\Memory\\ops_log.csv\"" }
  ]
}
```

---

## 6) Дальше едем сюда ⤵

### 6.1. Веб‑панель оператора (UI over FastAPI)
**Цель:** кнопки `/approve`, просмотр/редактирование `ProjectSpec.yml`, лента `ops_log.csv`, ручной запуск шагов.  
**Технологии:** FastAPI + Jinja/HTMX или простая React‑панель; auth через shared‑secret/локальный доступ.

**План:**
1. `/ui` — список последних операций (из `ops_log.csv`).
2. `/ui/specs` — список/редактирование `ProjectSpec.yml` (версионирование копиями).
3. `/ui/run?spec=...` — запуск, realtime‑лог (SSE/long‑poll).
4. `/ui/approvals` — очередь подтверждений (кнопка Approve).

### 6.2. Роли и политики
- Роли: `readonly`, `operator`, `admin`.
- Политики на команды (`/run`, `/write`, `/kill`) и каталоги.
- Отчёты об операциях по ролям.

### 6.3. Планировщик / расписания
- `ProjectSpec` с RRULE (cron‑подобно).
- Уведомления в Telegram о старте/финише, алерты при ошибках, авто‑retry.

### 6.4. Релиз под ключ
- Сборка артефактов, упаковка в ZIP/инсталлятор.
- Автоматический отчёт (лог, чек‑лист, артефакты) и публикация (S3/диск).

> Хочешь — подготовлю **Step 4** сразу: веб‑панель (UI) + роли + планировщик. Всё также упакую в .md для Cursor с файлами и тасками.

---

## 7) Быстрый чек‑лист

- [ ] Убрали `System32` из whitelist.
- [ ] Перегенерировали секреты (API + Telegram).
- [ ] API возвращает 401 без секрета и 200 с секретом.
- [ ] ProjectSpec успешно проходит, логи пишутся.
- [ ] Решили, куда движемся дальше: **UI + Роли** или **Планировщик**.

**Мы на рельсах. Дайте команду — упакую Step 4 (UI + Роли + Планировщик) таким же .md для Cursor.**
