# ⚡ Боевой запуск (3 шага)

1. Открой в Cursor папку: `D:\AI-Agent`
2. Проверь `.vscode\settings.json` — поле `"AI_AGENT_HTTP_SECRET"` должно быть **твоим длинным секретом**.
3. `Ctrl+Shift+P` → **Tasks: Run Task** → **AA: Start API**
   Ожидаем в терминале: `Uvicorn running on http://127.0.0.1:8088`.

# ✅ Контрольные проверки

## 1. **Health**
- `Ctrl+Shift+P` → **AA: Health Check** → должно вернуть: `{"status":"ok"}`

## 2. **Команда (натуральный язык)**
- `Ctrl+Shift+P` → **AA: Command (prompt)**
- Введи: `где я`
- Ожидаем путь рабочей директории (D:\AI-Agent)

## 3. **LLM-роутер**
- **AA: Command (prompt)** → `ответь одним словом: pong`
- Ожидаем: `pong`
- Если пусто → проверь `LMSTUDIO_MODEL` в `.vscode\settings.json` или задай `OPENAI_API_KEY/OPENAI_MODEL` для fallback

## 4. **Approvals (безопасность)**
- **AA: Approvals Pending** → ожидаем `[]` (если заявок нет)

## 5. **Project Runner (demo)**
- **AA: Project Validate (prompt path)** → `D:/AI-Agent/Projects/demo/ProjectSpec.yml`
- **AA: Project Run (prompt id)** → `demo`
- **AA: Project Status (prompt id)** → `demo`
- Ожидаем: `state=done`, прогресс на 100%

## 6. **Скаффолдинг проекта**
- **🔥 AA: Scaffold FastAPI+Postgres**
- Ожидаем создание `D:\Projects\fastapi-starter\...`
- Затем (по желанию) валидация/запуск этого ProjectSpec через пункты 5a–5c

# 🧪 Быстрый smoke в терминале (если нужно руками)

```powershell
$h=@{"x-agent-secret"=$env:AI_AGENT_HTTP_SECRET}
irm http://127.0.0.1:8088/health
$body=@{ text="где я"; session="TG" } | ConvertTo-Json -Compress
irm -Method Post http://127.0.0.1:8088/command -Headers $h -Body $body -ContentType 'application/json; charset=utf-8'
```

# 🛠 Troubleshooting (самые частые)

## **401 Unauthorized**
Проверь, что секрет в `.vscode\settings.json` и заголовок `x-agent-secret` совпадают.
В задачах уже используется переменная `AI_AGENT_HTTP_SECRET`.

## **API не стартует / порт занят**
```powershell
Get-Process | ? {$_.ProcessName -match "python|uvicorn"} | Stop-Process -Force
```
затем снова **AA: Start API**.

## **Кириллица / Unicode**
У нас в скриптах выставлен UTF-8; если где-то увидишь `latin-1`, запускай Python с `-X utf8` и убедись, что запросы идут `Content-Type: application/json; charset=utf-8`.

## **LM Studio "думает молча"**
Укажи точный `LMSTUDIO_MODEL` (как в `/v1/models` LM Studio).
Или задай `OPENAI_API_KEY`, `OPENAI_MODEL` — заработает fallback.

## **Операции требуют подтверждения**
Запроси список: **AA: Approvals Pending**, затем подтверди через `/approve <ID>` (в Телеграме или через нашу команду).

---

# 📋 Отчёт о тестировании

После прогона пришли короткий отчёт по каждому пункту (1–6): **✅/❌ + 1 строка вывода**. 
Если где-то ❌ — сразу приложи кусок лога/ответ. Разрулим.

## Пример отчёта:
```
1. Health: ✅ {"status":"ok"}
2. Команда: ✅ "D:\AI-Agent"
3. LLM: ✅ "pong"
4. Approvals: ✅ []
5. Project Runner: ✅ "state":"done"
6. Scaffold: ✅ "D:\Projects\fastapi-starter создан"
```

**Готов к бою!** 🚀

