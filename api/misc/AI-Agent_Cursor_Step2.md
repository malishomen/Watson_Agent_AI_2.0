# Cursor — ТЗ и инструкции: от идеи к «под ключ» (WORKDIR, ProjectSpec, Runner)

> **Цель:** мы с Вами — МОЗГ, ПК‑агент — ИСПОЛНИТЕЛЬ. В этом документе — полный пакет для Cursor: фикс постоянной рабочей директории, шаблон ТЗ `ProjectSpec.yml`, исполнитель `run_project.py` и задачи для автозапуска из Cursor.

---

## 0) Что уже готово
- LM Studio слушает `http://127.0.0.1:1234`, модель `deepseek-r1-distill-qwen-14b-abliterated-v2` активна.
- venv: `D:\AI-Agent\venv` (активируем через `D:\AI-Agent\venv\Scripts\Activate.ps1`).
- Переменные окружения заданы: `LM_STUDIO_URL`, `LM_STUDIO_MODEL`, `AGENT_DB`.
- Агент: `D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py` (SQLite‑память, fallback к OpenAI, заметки).
- Расширенные команды: `/run`, `/read`, `/write`, `/kill`, `/cd`, `/pwd`, `/approve` + лог операций.

---

## 1) Фикс `/cd`: постоянная рабочая директория (WORKDIR) между запусками

**Проблема:** `WORKDIR` был глобальной переменной процесса → при одноразовом запуске терялся.
**Решение:** сохраняем и читаем `WORKDIR` из SQLite‑таблицы `settings`.

### 1.1. Патч к `GPT+Deepseek_Agent_memory.py`

**A) Добавить таблицу `settings` в DDL** (внутри многострочной переменной `DDL = \"\"\" ... \"\"\"`):
```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**B) Добавить функции чтения/записи настроек** (выше секции Orchestrator):
```python
def get_setting(key: str, default: str | None = None) -> str | None:
    with db_connect() as c:
        row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

def set_setting(key: str, value: str) -> None:
    with db_connect() as c:
        c.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        c.commit()
```

**C) Подхватывать `WORKDIR` из БД при старте** (внутри `main()`, СРАЗУ после `init_db()` и получения `sid`):
```python
init_db()
sid = get_or_create_session(args.session)

db_workdir = get_setting("workdir")
if db_workdir:
    from pathlib import Path as _Path
    try:
        global WORKDIR
        WORKDIR = _Path(db_workdir).resolve()
    except Exception:
        pass
```

**D) Сохранять `WORKDIR` в БД при `/cd`** (в функции `set_cwd`):
```python
def set_cwd(path: str) -> str:
    global WORKDIR
    p = Path(path).resolve()
    if not is_path_allowed(p):
        aid = new_approval("set_cwd", {"path": path})
        return f"Требуется подтверждение: /approve {aid}"
    WORKDIR = p
    try:
        set_setting("workdir", str(WORKDIR))
    except Exception:
        pass
    return f"OK: WORKDIR={WORKDIR}"
```

**Проверка:**
```powershell
# 1) сохранить рабочую директорию
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/cd D:\AI-Agent\Memory"
# 2) убедиться
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/pwd"
# 3) закрыть окно, открыть новое и снова проверить
python D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py --session "Danil-PC" --once "/pwd"
```

---

## 2) Шаблон ТЗ проекта — `D:\AI-Agent\ProjectSpec.yml`

Сохраните файл с содержимым ниже. Это минимальный пример «под ключ»: записать файл, прочитать, открыть Блокнот и закрыть. Включён шаг за пределами белого списка для теста `/approve`.

```yaml
name: "Demo Project — Hello Agent"
description: "Показательный прогон: создать файл, прочесть его, запустить блокнот, закрыть."

defaults:
  session: "Danil-PC"
  base_dir: "D:\\AI-Agent\\Memory"

steps:
  - action: cd
    path: "D:\\AI-Agent\\Memory"

  - action: write
    path: "D:\\AI-Agent\\Memory\\hello.txt"
    text: "Привет, Данил! Это автозапуск по ТЗ."

  - action: read
    path: "D:\\AI-Agent\\Memory\\hello.txt"

  - action: run
    exe: "C:\\Windows\\System32\\notepad.exe"
    args: "\"D:\\AI-Agent\\Memory\\hello.txt\""

  - action: kill
    target: "notepad"

  # шаг вне белого списка — должен запросить approve
  - action: write
    path: "C:\\temp\\outside.txt"
    text: "Это проверка безопасности."
    expect_approve: true
```

---

## 3) Исполнитель ТЗ — `D:\AI-Agent\run_project.py`

Этот скрипт читает YAML и пошагово вызывает Вашего агента через `--once`‑команды.
**Требуется** пакет `PyYAML` (`pip install pyyaml`).

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, sys, yaml
from pathlib import Path

AGENT = r"D:\\AI-Agent\\Memory\\GPT+Deepseek_Agent_memory.py"

def call_agent(session: str, command: str) -> int:
    cmd = ["python", AGENT, "--session", session, "--once", command]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode

def main():
    if len(sys.argv) < 2:
        print("Usage: run_project.py D:\\AI-Agent\\ProjectSpec.yml")
        return 2

    spec_path = Path(sys.argv[1]).resolve()
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    session = data.get("defaults", {}).get("session", "Danil-PC")
    steps = data.get("steps", [])
    rc_total = 0

    for i, step in enumerate(steps, 1):
        action = step.get("action")
        print(f"\n=== Step {i}: {action} ===")

        if action == "cd":
            path = step["path"]
            rc_total |= call_agent(session, f"/cd {path}")

        elif action == "pwd":
            rc_total |= call_agent(session, "/pwd")

        elif action == "write":
            path, text = step["path"], step.get("text", "")
            rc_total |= call_agent(session, f"/write {path} ::: {text}")

        elif action == "read":
            path = step["path"]
            rc_total |= call_agent(session, f"/read {path}")

        elif action == "run":
            exe = step["exe"]
            args = step.get("args", "")
            qexe = f"\"{exe}\"" if (" " in exe and not exe.startswith("\"")) else exe
            rc_total |= call_agent(session, f"/run {qexe} {args}".strip())

        elif action == "kill":
            target = step["target"]
            rc_total |= call_agent(session, f"/kill {target}")

        else:
            print(f"Неизвестное действие: {action}")
            rc_total |= 1

    print("\n=== DONE ===")
    sys.exit(rc_total)

if __name__ == "__main__":
    main()
```

**Установка зависимости (один раз):**
```powershell
pip install pyyaml
```

---

## 4) Cursor — задачи (tasks.code.json)

Добавьте **к существующим** ещё два блока в `D:\AI-Agent\cursor\tasks.code.json`:

```json
{
  "title": "Agent: set workdir to Memory",
  "description": "Сохранить рабочую директорию для будущих запусков",
  "steps": [
    { "type": "terminal", "command": "python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session Danil-PC --once \"/cd D:\\AI-Agent\\Memory\"" },
    { "type": "terminal", "command": "python D:/AI-Agent/Memory/GPT+Deepseek_Agent_memory.py --session Danil-PC --once \"/pwd\"" }
  ]
},
{
  "title": "Project: run spec",
  "description": "Запуск сценария из ProjectSpec.yml",
  "steps": [
    { "type": "terminal", "command": "pip install pyyaml" },
    { "type": "terminal", "command": "python D:/AI-Agent/run_project.py D:/AI-Agent/ProjectSpec.yml" }
  ]
}
```

> В Cursor: **Run Task → Project: run spec** → контролируйте вывод. На шаге вне белого списка получите запрос `/approve AP-...`.

---

## 5) Чек‑лист после внедрения
- [ ] `/cd` сохраняет `WORKDIR` и это видно после повторного запуска `/pwd` (даже в новом окне).
- [ ] `ProjectSpec.yml` на месте и валиден.
- [ ] `run_project.py` запускается и выполняет все шаги.
- [ ] На шаге вне белого списка — появляется запрос `/approve` и после подтверждения операция проходит.
- [ ] `ops_log.csv` фиксирует все операции.
- [ ] Cursor‑таски видны и работают.

---

## 6) Дальше к «под ключ»
- **FastAPI‑режим агента** (долгоживущий процесс: состояние без БД, web‑панель).
- **Telegram‑оператор** (удалённые approvals, статусы, алерты).
- **Роли/политики** (белые списки, лимиты, отчёты).
- **Генератор релизов** (сборка артефактов/инсталлятор, упаковка, публикация).

> Готов подготовить следующий пакет: FastAPI‑обвязка + Telegram‑оператор. Скажите «поехали» — и положу новый .md для Cursor с кодом и задачами.
