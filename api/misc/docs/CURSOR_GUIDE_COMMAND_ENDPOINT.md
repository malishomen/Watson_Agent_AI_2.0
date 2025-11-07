# CURSOR: /command + универсальный парсер (RU/EN) → агент/терминал/Cursor

## Задача

Сделать так, чтобы из Telegram (и не только) можно было отправить **любую фразу** (рус/англ), а система:

1. нормализовала её в понятную команду,
2. прогнала через **Approval-страж** при необходимости,
3. выполнила через **ПК-агента** или **терминал** (и опционально через **Cursor**),
4. вернула результат в Telegram.

---

## Архитектура (кратко)

* **FastAPI `/command`** — единая точка входа (принимает любую строку).
* **Парсер `nlp_command_router.py`** — превращает фразы в команды `/run|/read|/write|/kill|/cd|/pwd` или в терминальные задачи.
* **ПК-агент** — уже умеет эти команды и `/approve AP-..`.
* **Безопасность** — заголовок `x-agent-secret`, белые списки путей, логи, approvals.

---

## 1) Добавляем парсер: `parsers/nlp_command_router.py`

```python
# parsers/nlp_command_router.py
# Простой гибридный парсер: RU/EN → нормализованные команды агента/терминала.
import re
from pathlib import Path

# быстрые словари синонимов
RUN_WORDS = r"(запусти|запуск|открой|run|start|launch)"
READ_WORDS = r"(прочитай|прочитать|read|show\s+file|cat|type)"
WRITE_WORDS = r"(запиши|записать|добавь|write|append)"
KILL_WORDS = r"(убей|останови|kill|terminate|stop\s+process)"
PWD_WORDS = r"(где\s+я|рабочая\s+директория|pwd|where\s+am\s+i)"
CD_WORDS  = r"(перейди\s+в|сменить\s+директорию|cd|chdir)"
PROC_LIST = r"(покажи\s+процессы|список\s+процессов|tasklist|process\s+list)"
GPU_TEMP  = r"(температуру\s+gpu|gpu\s*temp|gpu\s*temperature)"

def _quote(path: str) -> str:
    if not path:
        return path
    p = path.strip()
    if " " in p and not (p.startswith('"') and p.endswith('"')):
        return f'"{p}"'
    return p

def parse_free_text(text: str) -> str:
    """
    Возвращает нормализованную команду для агента:
    - /run "exe" [args]
    - /read D:\file.txt
    - /write D:\file.txt ::: TEXT
    - /kill notepad.exe | /kill 1234
    - /cd D:\workdir
    - /pwd
    - /cursor/terminal <command>  (как backoff)
    Если текст уже начинается с '/', возвращаем как есть.
    """
    if not text:
        return "/pwd"

    t = text.strip()
    low = t.lower()

    # Уже нормальная команда?
    if low.startswith("/"):
        return t

    # 1) процессы
    if re.search(PROC_LIST, low):
        return '/cursor/terminal tasklist'

    # 2) GPU температура (пример свободного навыка → терминал)
    if re.search(GPU_TEMP, low):
        # nvidia-smi у NVIDIA; под AMD адаптировать (radeon-profile-cli и т.п.)
        return '/cursor/terminal nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'

    # 3) run
    if re.search(RUN_WORDS, low):
        # эвристика: вытащим слово после глагола
        m = re.search(RUN_WORDS + r"\s+(.+)$", low)
        if m:
            payload = m.group(1).strip()
            # если путь .exe или .bat/.cmd
            if re.search(r"\.(exe|bat|cmd|ps1)\b", payload):
                return f'/run {_quote(payload)}'
            # иначе попробуем как имя программы
            return f'/run "{payload}"'
        return '/run "notepad.exe"'

    # 4) read
    if re.search(READ_WORDS, low):
        # извлечь путь (наивно)
        m = re.search(r"([a-z]:\\[^<>:\"|?*]+)", t, re.IGNORECASE)
        if m:
            return f"/read {m.group(1)}"
        return "/read D:\\AI-Agent\\README.md"

    # 5) write
    if re.search(WRITE_WORDS, low):
        # формат: "запиши в D:\file.txt: текст ..."
        m = re.search(r"в\s+([a-z]:\\[^<>:\"|?*]+)\s*[:\-—]\s*(.+)$", t, re.IGNORECASE)
        if m:
            path, body = m.group(1).strip(), m.group(2).strip()
            return f"/write {path} ::: {body}"
        # запасной вариант
        return '/write D:\\AI-Agent\\notes.txt ::: Добавлено из свободной команды'

    # 6) kill
    if re.search(KILL_WORDS, low):
        m = re.search(KILL_WORDS + r"\s+(.+)$", low)
        if m:
            target = m.group(1).strip().strip('"')
            return f"/kill {target}"
        return "/kill notepad.exe"

    # 7) pwd
    if re.search(PWD_WORDS, low):
        return "/pwd"

    # 8) cd
    if re.search(CD_WORDS, low):
        m = re.search(CD_WORDS + r"\s+([a-z]:\\[^<>:\"|?*]+)$", t, re.IGNORECASE)
        if m:
            return f"/cd {m.group(1).strip()}"
        return "/cd D:\\AI-Agent"

    # 9) fallback → терминал или диалог LLM
    # Сначала попробуем терминал "как есть" (осторожно!)
    # Можно включать только по ключевому слову, но для демонстрации оставим так:
    if low.startswith("терминал ") or low.startswith("terminal "):
        cmd = t.split(" ", 1)[1]
        return f"/cursor/terminal {cmd}"

    # Иначе отдаём на обычный агентный диалог (LLM)
    return t  # пусть respond обработает как обычный чат
```

> Парсер намеренно «прост», но расширяемый: добавляй правила/синонимы по мере использования.

---

## 2) Новый эндпоинт FastAPI: `POST /command`

В `api/fastapi_agent.py` (или где у тебя FastAPI-роуты):

```python
# api/fastapi_agent.py (фрагмент)
from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
import os

from parsers.nlp_command_router import parse_free_text
from Memory.GPT+Deepseek_Agent_memory import (
    init_db, get_or_create_session, respond
)

app = FastAPI()

# ---- Безопасность (у тебя уже есть похожая проверка) ----
def verify_secret(x_agent_secret: str = Header(...)):
    expected = os.getenv("AGENT_HTTP_SHARED_SECRET", "").strip()
    got = (x_agent_secret or "").strip()
    if not expected or got != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class CommandIn(BaseModel):
    text: str
    session: str | None = "Telegram"   # можно передавать chat_id/username
    mode: str | None = None            # future: "agent"/"terminal"/"cursor"

class CommandOut(BaseModel):
    ok: bool
    normalized: str
    result: str

@app.post("/command", response_model=CommandOut)
def command_endpoint(payload: CommandIn, _=Depends(verify_secret)):
    """
    Принимает произвольный текст → нормализует → гонит в respond(...)
    """
    init_db()
    session = payload.session or "Telegram"
    sid = get_or_create_session(session)

    user_text = payload.text or ""
    # Если текст уже slash-команда — оставляем, иначе парсим
    normalized = user_text if user_text.strip().startswith("/") else parse_free_text(user_text)

    try:
        result = respond(sid, normalized)
        return CommandOut(ok=True, normalized=normalized, result=result)
    except Exception as e:
        return CommandOut(ok=False, normalized=normalized, result=f"Ошибка: {e}")
```

---

## 3) Интеграция с Telegram-ботом

В обработчике апдейтов бота (любой Python-бот-фреймворк), делаем форвард на `/command`:

```python
import requests
import os

API_URL = "http://127.0.0.1:8088/command"
SECRET  = os.getenv("AGENT_HTTP_SHARED_SECRET", "")

def send_to_agent(text: str, session: str = "Telegram") -> str:
    headers = {"x-agent-secret": SECRET}
    data = {"text": text, "session": session}
    r = requests.post(API_URL, json=data, headers=headers, timeout=30)
    try:
        j = r.json()
        if j.get("ok"):
            # Можно красиво отдать и normalized, и result
            return f"→ {j.get('normalized')}\n\n{j.get('result')}"
        else:
            return f"Ошибка: {j.get('result')}"
    except Exception:
        return f"HTTP {r.status_code}: {r.text}"
```

Теперь **любой текст** из Telegram идёт в `/command`.
Примеры:

* `запусти notepad` → `/run "notepad"`
* `покажи процессы` → `/cursor/terminal tasklist`
* `/read D:\AI-Agent\README.md` → как есть

---

## 4) Безопасность и approvals (напоминание)

* Все «опасные» пути вне белого списка → возвращают `Требуется подтверждение: /approve AP-XXXX`.
* Ты подтверждаешь в Telegram: `/approve AP-XXXX`.
* Агент выполняет действие и логирует в `D:\AI-Agent\Memory\ops_log.csv`.

---

## 5) Смоук-тесты

### PowerShell (локально)

```powershell
# 1) Health
irm http://127.0.0.1:8088/health

# 2) Простой текст → нормализация → выполнение
$h = @{ "x-agent-secret" = $env:AGENT_HTTP_SHARED_SECRET }
$body = @{ text="запусти notepad"; session="TG-Danil" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json' -Body $body

# 3) Показать процессы
$body = @{ text="покажи процессы"; session="TG-Danil" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json' -Body $body

# 4) Прочитать файл (в белом списке)
$body = @{ text="/read D:\AI-Agent\README.md"; session="TG-Danil" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json' -Body $body

# 5) Запись вне белого списка → ожидаем /approve
$body = @{ text="/write C:\temp\test.txt ::: hi"; session="TG-Danil" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json' -Body $body

# 6) Подтвердить
# возьми ID из ответа шага (5)
$body = @{ text="/approve AP-1727356123456"; session="TG-Danil" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/command -Headers $h -ContentType 'application/json' -Body $body
```

---

## 6) Troubleshooting (быстрый)

* **401 Unauthorized** → проверь, что Telegram-воркер шлёт заголовок `x-agent-secret`, совпадающий с процессом uvicorn.
* **Cursor 503** → мост не активирован (это ок, если ты его ещё не включал).
* **Модель «молчит»** → у нас уже есть очистка `<think>…</think>` и fallback в пайплайне v2; убедись, что LM Studio сервер активен и `model_id` верный.
* **Пути и права** → операции вне whitelisted директорий требуют `/approve`.

---

## 7) Расширение парсера (идеи)

* Добавить больше синонимов: «проверь память», «сеть пингани гугл», «покажи ip» → маппить на терминальные команды (`Get-ComputerInfo`, `ping 8.8.8.8`, `ipconfig` и т.п.).
* Детект языков (langid) и ветки правил по языку.
* «Слоты»: `замени в файле X строку Y на Z` → генерация `/cursor/terminal` c безопасным PowerShell-скриптом.

---

## 8) Что уже есть (напоминание)

* Белые списки: `D:\AI-Agent`, `D:\Projects`, `D:\Temp`.
* Логи: `D:\AI-Agent\Memory\ops_log.csv` (авто-хедер).
* Команды: `/run`, `/read`, `/write`, `/kill`, `/cd`, `/pwd`, `/approve`.
* Заметки в SQLite: `add_note`, `fetch_last_note`, `fetch_notes`.
* Зачистка reasoning в LLM: `strip_reasoning()`.

---

## Финалка

Теперь бот принимает **любые твои фразы** (и мои подсказки), парсер их нормализует, а агент **исполняет**.
Опасные действия — только через `/approve`. Логи — в CSV.
Дальше подключаем APScheduler и `ProjectSpec.yml` — и будет настоящий «под ключ».

**Короткий девиз:** думай свободно, исполняй безопасно. 🚀
