# 🔄 Cursor ↔ Watson Agent Integration Status

## ✅ WORKING: Cursor → Agent

### Направление: Cursor IDE → Watson API

**Endpoints:**
- `POST /command` - универсальные команды
- `POST /autocode/generate` - генерация кода
- `POST /relay/submit` - маршрутизация задач
- `POST /agent/respond` - диалог с агентом

**Конфигурация:**
```powershell
$env:WATSON_API_BASE = "http://127.0.0.1:8090"
$env:AGENT_HTTP_SHARED_SECRET = "test123"
```

**Примеры использования:**

```powershell
# Отправить задачу из Cursor
$headers = @{ "x-agent-secret" = "test123" }
$body = @{
    task = "Add logging to authentication module"
    dry_run = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8090/autocode/generate" `
  -Method POST -Headers $headers -ContentType "application/json" -Body $body
```

**Status:** ✅ **FULLY FUNCTIONAL**

---

## ⚠️ NOT WORKING: Agent → Cursor

### Направление: Watson API → Cursor IDE

**Проблема:**
```
HTTPConnectionPool(host='127.0.0.1', port=3000): Max retries exceeded
Failed to establish a new connection: [WinError 10061]
```

**Причина:**
🚫 **Cursor IDE не предоставляет HTTP API для внешнего управления**

**Configured Endpoints (теоретические):**
- `/cursor/open` - открыть файл
- `/cursor/insert` - вставить текст
- `/cursor/replace` - заменить текст
- `/cursor/save` - сохранить файл
- `/cursor/create` - создать файл
- `/cursor/terminal` - запустить команду в терминале
- `/cursor/task` - запустить task
- `/cursor/chat` - отправить в Cursor Chat
- `/cursor/project` - открыть проект

**Текущая конфигурация:**
```powershell
$env:CURSOR_API_URL = "http://127.0.0.1:3000"  # ❌ Не слушается
$env:CURSOR_API_KEY = "cursor_key_1922"        # ❌ Не используется
```

**Status:** ❌ **NOT AVAILABLE** (Cursor IDE limitation)

---

## 🔧 ALTERNATIVE SOLUTIONS

### Solution 1: UI Automation (Available Now!)

Используйте `api/cursor_automation_agent.py`:

```python
from api.cursor_automation_agent import CursorAutomationAgent

agent = CursorAutomationAgent(
    project_path="D:/projects/MyProject",
    secret="test123"
)

# Открыть Cursor и выполнить задачу
agent.start_cursor()
agent.focus_cursor_window()
agent.send_task_to_cursor("Add logging to function X")
```

**Преимущества:**
- ✅ Работает сейчас без изменений Cursor
- ✅ Полный контроль через UI automation
- ✅ Может нажимать кнопки, вводить текст

**Недостатки:**
- ⚠️ Требует активного окна Cursor
- ⚠️ Зависит от UI элементов

### Solution 2: Cursor Extension (Recommended)

Создать расширение для Cursor:

```typescript
// extensions/watson-bridge/src/extension.ts
import * as vscode from 'vscode';
import * as http from 'http';

export function activate(context: vscode.ExtensionContext) {
    // Создать HTTP сервер для приема команд
    const server = http.createServer(async (req, res) => {
        if (req.method === 'POST' && req.url === '/v1/editor/open') {
            const data = await parseBody(req);
            const doc = await vscode.workspace.openTextDocument(data.filepath);
            await vscode.window.showTextDocument(doc);
            res.writeHead(200);
            res.end(JSON.stringify({ ok: true }));
        }
    });
    
    server.listen(3000);
    console.log('Watson Bridge listening on port 3000');
}
```

**Установка:**
1. Создать расширение в `~/.cursor/extensions/watson-bridge`
2. Перезапустить Cursor
3. Расширение откроет порт 3000

### Solution 3: File-Based Communication

Использовать файловую систему для обмена:

```python
# Watson Agent записывает задачи
with open("D:/temp/cursor_tasks/task_001.json", "w") as f:
    json.dump({
        "action": "open_file",
        "filepath": "D:/projects/MyProject/main.py",
        "line": 42
    }, f)

# Cursor расширение мониторит папку и выполняет задачи
```

**Преимущества:**
- ✅ Надежно
- ✅ Не требует сетевого подключения

**Недостатки:**
- ⚠️ Задержка (polling)
- ⚠️ Требует расширение

---

## 📝 CURRENT RECOMMENDATIONS

### ✅ Используйте сейчас:

1. **Cursor → Agent** (работает из коробки)
   ```powershell
   # Отправить задачу агенту
   .\Send-Task.ps1 -Task "Refactor function X"
   ```

2. **UI Automation** для Agent → Cursor
   ```python
   # Автоматизация Cursor через pyautogui
   from api.cursor_automation_agent import CursorAutomationAgent
   ```

### 🔮 Для будущего:

1. Создать **Cursor Extension** для двусторонней связи
2. Опубликовать в Cursor Marketplace
3. Настроить WebSocket для real-time коммуникации

---

## 🧪 TESTING

### Test Cursor → Agent:

```powershell
# Health check
curl http://127.0.0.1:8090/health

# Send task
$body = @{ task = "Test task"; dry_run = $true } | ConvertTo-Json
curl -X POST http://127.0.0.1:8090/autocode/generate `
  -H "Content-Type: application/json" `
  -H "x-agent-secret: test123" `
  -d $body
```

**Expected:** ✅ 200 OK with diff output

### Test Agent → Cursor:

```powershell
# Try to open file in Cursor
$body = @{ filepath = "D:/test.txt" } | ConvertTo-Json
curl -X POST http://127.0.0.1:8090/cursor/open `
  -H "Content-Type: application/json" `
  -H "x-agent-secret: test123" `
  -d $body
```

**Expected:** ❌ 503 Service Unavailable (Cursor API not available)

---

## 📊 SUMMARY

| Feature | Status | Notes |
|---------|--------|-------|
| Cursor → Agent | ✅ Works | Full API available |
| Agent → Cursor HTTP | ❌ Not Available | Cursor doesn't provide API |
| Agent → Cursor UI | ✅ Available | Via cursor_automation_agent.py |
| Agent → Cursor Extension | 🔮 Future | Needs development |

---

## 🔗 REFERENCES

- API Documentation: `QUICKSTART.md`
- Cursor Integration Guide: `api/misc/docs/CURSOR_GUIDE_COMMAND_ENDPOINT.md`
- UI Automation: `api/cursor_automation_agent.py`
- Cursor Bridge: `api/misc/cursor_bridge/`

---

**Last Updated:** 2025-11-07  
**Watson Agent Version:** 2.0  
**Status:** Production Ready (one-way communication)

