# Cursor — Инструкции по расширению агента (Windows-команды + безопасность)

> **Цель**: добавить в локальный ИИ‑агент навыки управления Windows и защиту операций, чтобы двигаться к режиму «под ключ».  
> **Ключевой файл**: `D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py`

---

## 0) Что уже готово
- LM Studio (порт 1234) и модель `deepseek-r1-distill-qwen-14b-abliterated-v2`.
- Виртуальное окружение: `D:\AI-Agent\venv`.
- Переменные окружения: `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `AGENT_DB`.
- Скрипт агента работает (память SQLite, сессии, fallback).
- Команды памяти: `/remember`, `/recall`, `/notes`.

---

## 1) Что добавляем в этом патче
**Новые команды пользователя**:
- `/run "C:\Path\app.exe" --opt1` — запустить программу
- `/read D:\path\file.txt` — прочитать файл
- `/write D:\path\file.txt ::: ТЕКСТ` — записать файл
- `/kill notepad.exe` **или** `/kill 1234` — остановить процесс
- `/cd D:\workdir` и `/pwd` — рабочая директория
- `/approve AP-...` — подтверждение опасного действия

**Безопасность и логирование**:
- Белый список директорий (по умолчанию): `D:\AI-Agent`, `D:\Projects`, `D:\Temp`  
  Все операции **вне** белого списка требуют подтверждения `/approve`.
- Журнал операций в `D:\AI-Agent\Memory\ops_log.csv`.
- Фильтрация «скрытых мыслей» `<think>...</think>` из ответа модели.

---

## 2) Патч-коды (вставить в `GPT+Deepseek_Agent_memory.py`)

### 2.1 Импорты (рядом с остальными)
```python
import subprocess, csv, re
from pathlib import Path
```

### 2.2 Константы политики (после существующих конфигов)
```python
WORKDIR = Path(os.getenv("AGENT_WORKDIR", "D:\\AI-Agent")).resolve()
WHITELIST_DIRS = [Path("D:\\AI-Agent").resolve(), Path("D:\\Projects").resolve(), Path("D:\\Temp").resolve()]
OPS_LOG = Path(os.getenv("AGENT_OPS_LOG", "D:\\AI-Agent\\Memory\\ops_log.csv")).resolve()
PENDING_APPROVALS = {}  # id -> dict(action=..., params=..., created_at=...)
```

### 2.3 Фильтрация мыслей модели (выше секции Orchestrator)
```python
def strip_reasoning(text: str) -> str:
    if not text:
        return text
    return re.sub(r"<think>[\\s\\S]*?</think>", "", text, flags=re.IGNORECASE).strip()
```
И замените возврат в `chat_lm_studio` и `chat_openai`:
```python
# было:
# return data["choices"][0]["message"]["content"].strip()
# стало:
return strip_reasoning(data["choices"][0]["message"]["content"].strip())
```

### 2.4 DDL — добавить таблицу заметок (внутри строки DDL)
```sql
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notes_session_time ON notes(session_id, created_at);
```

### 2.5 Функции для заметок (выше Orchestrator)
```python
def add_note(session_id:int, content:str)->None:
    with db_connect() as c:
        c.execute("INSERT INTO notes(session_id, content, created_at) VALUES (?, ?, ?)",
                  (session_id, content, datetime.utcnow().isoformat()))
        c.commit()

def fetch_last_note(session_id:int)->str|None:
    with db_connect() as c:
        r = c.execute("SELECT content FROM notes WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
                      (session_id,)).fetchone()
        return r["content"] if r else None

def fetch_notes(session_id:int, limit:int=10)->list[str]:
    with db_connect() as c:
        rows = c.execute("SELECT content FROM notes WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                         (session_id, limit)).fetchall()
        return [x["content"] for x in rows]
```

### 2.6 Утилиты безопасности и логи (выше Orchestrator)
```python
def is_path_allowed(p: Path) -> bool:
    try:
        rp = p.resolve()
        return any(str(rp).startswith(str(base)) for base in WHITELIST_DIRS)
    except Exception:
        return False

def log_op(op: str, ok: bool, detail: str):
    OPS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OPS_LOG.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.utcnow().isoformat(), op, "OK" if ok else "FAIL", detail])

def need_approval_for_path(p: Path) -> bool:
    return not is_path_allowed(p)

def new_approval(action: str, params: dict) -> str:
    aid = f"AP-{int(time.time()*1000)}"
    PENDING_APPROVALS[aid] = {"action": action, "params": params, "created_at": datetime.utcnow().isoformat()}
    return aid
```

### 2.7 Навыки: run / read / write / kill / cd / pwd (выше Orchestrator)
```python
def run_exe(path: str, args: str = "", cwd: str | None = None) -> str:
    exe = Path(path)
    if need_approval_for_path(exe):
        return f"Требуется подтверждение: /approve {new_approval('run_exe', {'path': path, 'args': args, 'cwd': cwd})}"
    cmd = f'"{exe}" {args}'.strip()
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or str(WORKDIR), timeout=120)
        out = (r.stdout or "") + ("\nERR:\n" + r.stderr if r.stderr else "")
        log_op("run_exe", r.returncode == 0, f"{cmd} @ {cwd or WORKDIR}")
        return out.strip() or "(пусто)"
    except Exception as e:
        log_op("run_exe", False, f"{cmd} -> {e}")
        return f"Ошибка запуска: {e}"

def read_file(path: str) -> str:
    p = Path(path)
    try:
        if need_approval_for_path(p):
            return f"Требуется подтверждение: /approve {new_approval('read_file', {'path': path})}"
        text = p.read_text(encoding="utf-8", errors="ignore")
        log_op("read_file", True, str(p))
        return text
    except Exception as e:
        log_op("read_file", False, f"{p} -> {e}")
        return f"Ошибка чтения: {e}"

def write_file(path: str, text: str) -> str:
    p = Path(path)
    try:
        if need_approval_for_path(p):
            return f"Требуется подтверждение: /approve {new_approval('write_file', {'path': path, 'text': text})}"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        log_op("write_file", True, str(p))
        return f"OK: записано {len(text)} символов в {p}"
    except Exception as e:
        log_op("write_file", False, f"{p} -> {e}")
        return f"Ошибка записи: {e}"

def stop_process(name_or_pid: str) -> str:
    try:
        cmd = (f"powershell -Command \"Stop-Process -Id {name_or_pid} -Force\"" if name_or_pid.isdigit()
               else f"powershell -Command \"Get-Process -Name '{name_or_pid}' -ErrorAction SilentlyContinue | Stop-Process -Force\"")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        ok = r.returncode == 0
        log_op("stop_process", ok, name_or_pid)
        return "OK" if ok else (r.stdout + "\n" + r.stderr).strip()
    except Exception as e:
        log_op("stop_process", False, name_or_pid + f" -> {e}")
        return f"Ошибка: {e}"

def set_cwd(path: str) -> str:
    global WORKDIR
    p = Path(path).resolve()
    if not is_path_allowed(p):
        return f"Требуется подтверждение: /approve {new_approval('set_cwd', {'path': path})}"
    WORKDIR = p
    return f"OK: WORKDIR={WORKDIR}"

def get_cwd() -> str:
    return str(WORKDIR)
```

### 2.8 Router команд (внутри `respond(...)`, сразу после `add_message(...)` и до вызова модели)
```python
    lower = user_text.strip().lower()

    if lower.startswith("/approve"):
        aid = (user_text.split(maxsplit=1)[1].strip() if len(user_text.split())>1 else "")
        item = PENDING_APPROVALS.pop(aid, None)
        if not item:
            reply = f"Заявка {aid or '?'} не найдена или уже подтверждена."
        else:
            act = item["action"]; params = item["params"]
            reply = (run_exe(params.get("path",""), params.get("args",""), params.get("cwd"))
                     if act=="run_exe" else
                     read_file(params.get("path","")) if act=="read_file" else
                     write_file(params.get("path",""), params.get("text","")) if act=="write_file" else
                     set_cwd(params.get("path","")) if act=="set_cwd" else
                     f"Неизвестное действие в заявке {aid}")
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/pwd"):
        reply = get_cwd(); add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/cd"):
        path = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = set_cwd(path) if path else "Синтаксис: /cd D:\\папка"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/run"):
        payload = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        if not payload:
            reply = "Синтаксис: /run \"C:\\путь\\app.exe\" [аргументы]"
        else:
            if payload.startswith('\"'):
                try: exe, rest = payload.split('\"', 2)[1], payload.split('\"', 2)[2].strip()
                except: exe, rest = payload.strip('\"'), ""
            else:
                parts = payload.split(" ", 1); exe, rest = parts[0], (parts[1] if len(parts) > 1 else "")
            reply = run_exe(exe, rest, None)
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/read"):
        path = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = read_file(path) if path else "Синтаксис: /read D:\\путь\\file.txt"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/write"):
        try:
            _, rest = user_text.split(" ", 1)
            fpath, text = rest.split(":::", 1)
            fpath, text = fpath.strip(), text.strip()
            if need_approval_for_path(Path(fpath)):
                reply = f"Требуется подтверждение: /approve {new_approval('write_file', {'path': fpath, 'text': text})}"
            else:
                reply = write_file(fpath, text)
        except ValueError:
            reply = "Синтаксис: /write D:\\путь\\file.txt ::: ТЕКСТ"
        add_message(session_id, "assistant", reply); return reply

    if lower.startswith("/kill"):
        target = user_text.split(" ", 1)[1].strip() if " " in user_text else ""
        reply = stop_process(target) if target else "Синтаксис: /kill notepad.exe ИЛИ /kill 1234"
        add_message(session_id, "assistant", reply); return reply
```

> Команды заметок `/remember`, `/recall`, `/notes` — оставьте как есть.

---

## 3) Тесты после внедрения (в venv)
```powershell
# 1) Чтение (в белой зоне)
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/read D:\AI-Agent\Memory\ops_log.csv"

# 2) Запись (в белой зоне)
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/write D:\AI-Agent\Memory\test.txt ::: Hello, Agent!"

# 3) Запись вне белого списка (ожидаем запрос /approve)
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/write C:\temp\test.txt ::: should require approval"

# 4) Подтверждение (подставьте реальный ID из ответа шага 3)
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/approve AP-XXXXXXXX"
```

---

## 4) Как двигаемся к «под ключ»
1) Формируем совместно **ProjectSpec.yml** (ТЗ).  
2) Агент читает YAML и исполняет шаги; опасные действия проходят через `/approve`.  
3) На выходе — артефакты (ZIP/инсталлер/доки) и журнал `ops_log.csv`.

**Готово к следующему шагу:** подготовить шаблон `ProjectSpec.yml`, скрипт `run_project.py` (парсер YAML → вызовы команд), и `cursor/tasks.code.json` для автозапуска из Cursor.
