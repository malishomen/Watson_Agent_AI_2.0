# 📘 README_step_by_step.md

## 🚀 Быстрый старт

### 1. Подготовка окружения

```powershell
cd D:\AI-Agent\scripts
.\setup_environment.ps1
```

Что делает:

* Генерирует секрет для FastAPI (`AGENT_HTTP_SHARED_SECRET`)
* Настраивает LM Studio API (`OPENAI_API_BASE` и `OPENAI_API_KEY`)
* Проверяет доступность LM Studio и FastAPI
* Создаёт `README.md`, если файла нет

---

### 2. Запуск FastAPI агента

```powershell
cd D:\AI-Agent\scripts
.\start_fastapi.ps1
```

После запуска в окне должно появиться:

```
Uvicorn running on http://127.0.0.1:8088
Application startup complete.
```

---

### 3. Проверка доступности сервисов

```powershell
# Проверка FastAPI
Invoke-RestMethod http://127.0.0.1:8088/health

# Проверка моделей LM Studio
Invoke-RestMethod http://127.0.0.1:1234/v1/models
```

---

### 4. Запуск полного пайплайна

```powershell
cd D:\AI-Agent\scripts
.\e2e_agent_pipeline_v2.ps1
```

Что произойдёт:

1. Проверка здоровья FastAPI
2. Запрос к LM Studio (LLM)
3. Очистка `<think>…</think>`
4. Fallback строка, если LLM молчит
5. Добавление строки в `README.md`

---

### 5. Проверка результата

```powershell
Get-Content D:/AI-Agent/README.md -Tail 5
```

Должна появиться свежая строка (например:

```
Next step: Test the agent pipeline and verify all components work correctly
```

---

### 6. (Опционально) Проверка моста к Cursor

```powershell
$h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
$body = @{ filepath='D:/AI-Agent/README.md' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/cursor/open -Headers $h -Body $body -ContentType 'application/json'
```

Если мост не включен → вернёт 503 (это нормально).
Если API Cursor настроен → файл реально откроется в Cursor.

---

## ⚙️ Полезные команды

Остановить uvicorn:

```powershell
Get-Process | ? {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force
```

Перезапустить FastAPI с ручным секретом:

```powershell
$env:AGENT_HTTP_SHARED_SECRET = "key-TEST123"
uvicorn api.fastapi_agent:app --host 127.0.0.1 --port 8088 --reload
```

---

## 📊 Контрольный список (каждый прогон)

* ✅ LM Studio сервер запущен (Menu → Server → Start)
* ✅ `.\start_fastapi.ps1` поднял uvicorn
* ✅ `irm http://127.0.0.1:8088/health` → ok
* ✅ `irm http://127.0.0.1:1234/v1/models` → показывает модель
* ✅ `.\e2e_agent_pipeline_v2.ps1` → строка дописана в README.md

---

💡 Совет: если где-то выскакивает `401 Unauthorized`, проверь, что секрет одинаковый у клиента и у процесса uvicorn:

```powershell
echo $env:AGENT_HTTP_SHARED_SECRET
```

---

**Афоризм напоследок:**
«Система — как оркестр: каждый инструмент должен звучать вовремя, но дирижёр всегда один — ты.» 🎼

---
