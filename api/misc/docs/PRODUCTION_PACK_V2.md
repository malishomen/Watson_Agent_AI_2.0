# 🚀 AI-Agent Production Pack v2 - "Под ключ"

**Полная автоматизация проектов от ТЗ до артефактов**

---

## 🎯 **Что умеет система "под ключ"**

### ✅ **Принимает естественные команды:**
- "запусти проект demo" → автоматически выполняет ProjectSpec.yml
- "статус проекта demo" → показывает прогресс и ошибки
- "создай FastAPI сервис" → генерирует полный стек

### ✅ **Выполняет проекты пошагово:**
- 📝 Создает файлы и папки
- 🐍 Запускает Python скрипты
- 🐳 Собирает Docker контейнеры
- 📦 Инициализирует Git репозитории
- 🔧 Настраивает виртуальные окружения

### ✅ **Контролирует безопасность:**
- 🛡️ Белые списки путей
- ⚠️ Автоматические approvals для опасных операций
- 📊 Логирование всех действий
- 💾 Персистентное состояние проектов

---

## 📡 **API Endpoints**

### Основные команды
- `POST /command` — универсальный парсер (рус/англ → команды)
- `GET /approvals/pending` — просмотр заявок на подтверждение

### Project Management
- `POST /project/validate` — валидация ProjectSpec.yml
- `POST /project/upload` — загрузка спецификации
- `POST /project/run` — запуск проекта
- `GET /project/status` — прогресс + ошибки

---

## ⚙️ **Orchestrator Architecture**

### `orchestrator/project_state.py`
```python
# Управление состоянием проектов
- load_state(project_id) — загрузка прогресса
- save_state(project_id, state) — сохранение состояния
- reset_state(project_id) — сброс проекта
```

### `orchestrator/project_runner.py`
```python
# Выполнение проектов по спецификации
- run_project(project_id, resume=True) — запуск проекта
- run_step(project_id, step, state) — выполнение шага
- Поддержка типов: file.write, shell, git, python.run, docker
```

---

## 📋 **ProjectSpec.yml Template**

### Базовый шаблон
```yaml
name: demo
description: "Описание проекта"
steps:
  - type: file.write
    path: D:/Projects/app/main.py
    text: |
      # Код приложения
      
  - type: shell
    cwd: D:/Projects/app
    command: python -m venv .venv
    
  - type: git.init
    cwd: D:/Projects/app
    
  - type: docker.build
    cwd: D:/Projects/app
    tag: myapp:latest
```

### Поддерживаемые типы шагов:
- `file.write` — создание файлов
- `file.append` — добавление в файлы
- `shell` — выполнение команд
- `git.init` — инициализация Git
- `git.commit` — коммит изменений
- `python.run` — запуск Python скриптов
- `docker.build` — сборка Docker образов
- `docker.run` — запуск контейнеров
- `wait` — пауза выполнения

---

## 🚀 **Быстрый старт**

### 1. Установка системы
```powershell
cd D:\AI-Agent
.\scripts\install_agent.ps1
```

### 2. Создание проекта
```powershell
# Создать ProjectSpec.yml
New-Item -Path "D:\AI-Agent\Projects\myproject" -ItemType Directory
# Скопировать шаблон и отредактировать
```

### 3. Запуск проекта
```powershell
$h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }

# Валидация
$body = @{ spec_path = "D:/AI-Agent/Projects/myproject/ProjectSpec.yml" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/validate -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# Запуск
$body = @{ project_id = "myproject"; resume = $true } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/project/run -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'

# Статус
irm "http://127.0.0.1:8088/project/status?project_id=myproject" -Headers $h
```

### 4. Через Telegram
```
"запусти проект myproject"
"статус проекта myproject"
"список проектов"
```

---

## 📱 **Telegram Integration**

### Естественные команды
- "запусти проект demo" → `/project.run demo`
- "статус проекта demo" → `/project.status demo`
- "список проектов" → `/project.list`

### Готовые хуки
```python
# В telegram_integration.py
def send_to_agent(text, session="Telegram"):
    # Отправка команды агенту
    # Автоматический парсинг проектных команд
```

---

## 🔐 **Безопасность**

### Белые списки путей
- ✅ `D:\AI-Agent` — основная папка
- ✅ `D:\Projects` — проекты
- ✅ `D:\Temp` — временные файлы
- ❌ `System32` — исключен

### Approvals система
- ⚠️ Опасные операции требуют `/approve`
- 💾 Персистентные approvals в SQLite
- 📊 Логирование в `ops_log.csv`
- 🔄 Состояние проектов в `state.json`

---

## 🎯 **Готовые ProjectSpec шаблоны**

### FastAPI + Docker
```yaml
name: fastapi-demo
description: "FastAPI сервис под ключ"
steps:
  - type: file.write
    path: D:/Projects/fastapi-app/main.py
    text: |
      from fastapi import FastAPI
      app = FastAPI()
      
      @app.get("/")
      def root():
          return {"message": "Hello, FastAPI!"}
  
  - type: shell
    cwd: D:/Projects/fastapi-app
    command: python -m venv .venv && .\.venv\Scripts\pip install fastapi uvicorn
  
  - type: file.write
    path: D:/Projects/fastapi-app/Dockerfile
    text: |
      FROM python:3.11-slim
      WORKDIR /app
      COPY . .
      RUN pip install fastapi uvicorn
      CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  
  - type: git.init
    cwd: D:/Projects/fastapi-app
  
  - type: git.commit
    cwd: D:/Projects/fastapi-app
    message: "init FastAPI app"
  
  - type: docker.build
    cwd: D:/Projects/fastapi-app
    tag: fastapi-demo:latest
```

### Python CLI + Tests
```yaml
name: cli-tool
description: "CLI утилита с тестами"
steps:
  - type: file.write
    path: D:/Projects/cli-tool/main.py
    text: |
      import argparse
      import sys
      
      def main():
          parser = argparse.ArgumentParser()
          parser.add_argument("--name", default="World")
          args = parser.parse_args()
          print(f"Hello, {args.name}!")
      
      if __name__ == "__main__":
          main()
  
  - type: file.write
    path: D:/Projects/cli-tool/test_main.py
    text: |
      import unittest
      from unittest.mock import patch
      from main import main
      
      class TestCLI(unittest.TestCase):
          def test_main(self):
              with patch('sys.argv', ['main.py', '--name', 'Test']):
                  main()
  
  - type: shell
    cwd: D:/Projects/cli-tool
    command: python -m venv .venv && .\.venv\Scripts\pip install pytest
  
  - type: shell
    cwd: D:/Projects/cli-tool
    command: python -m pytest test_main.py -v
```

---

## 📊 **Мониторинг и логи**

### Логи проектов
```powershell
# Состояние проекта
Get-Content "D:\AI-Agent\Projects\demo\state.json"

# Логи операций
Get-Content "D:\AI-Agent\Memory\ops_log.csv" | Select-Object -Last 10
```

### Статус системы
```powershell
# Быстрая проверка
.\scripts\quick_commands.ps1 -Action status

# Диагностика проектов
.\scripts\incident_playbook.ps1 -Action diagnose
```

---

## 🎯 **Что можно собирать "под ключ"**

### 1. **Веб-сервисы**
- FastAPI + PostgreSQL + Docker Compose
- Flask + Redis + Celery
- Django + MySQL + Nginx

### 2. **CLI утилиты**
- Python скрипты с аргументами
- Go утилиты с тестами
- Node.js CLI с npm пакетами

### 3. **Микросервисы**
- REST API с документацией
- GraphQL серверы
- WebSocket сервисы

### 4. **DevOps пайплайны**
- GitHub Actions CI/CD
- Docker multi-stage builds
- Kubernetes манифесты

### 5. **Документация**
- Sphinx + PDF/HTML
- MkDocs + GitHub Pages
- Jupyter notebooks

---

## 🚀 **СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!**

### ✅ **Все компоненты протестированы:**
- 🎯 Project Runner API работает
- 🤖 NLP Router понимает команды
- 📋 Orchestrator выполняет проекты
- 🔐 Безопасность настроена
- 📱 Telegram интеграция готова

### 🎯 **Готов к созданию любого проекта "под ключ"!**

**Просто скажи, что нужно собрать, и агент:**
1. 📝 Создаст ProjectSpec.yml
2. 🚀 Запустит выполнение
3. 📊 Покажет прогресс
4. 🎁 Выдаст готовые артефакты

---

*Создано: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")*  
*Версия: Production Pack v2.0 - "Под ключ"*
