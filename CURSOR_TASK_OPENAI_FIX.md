# ГЛОБАЛЬНАЯ ЗАДАЧА ДЛЯ CURSOR AI

Сделать полностью рабочую связку:

**Telegram-бот → конвеер (/relay/submit) → OpenAI Chat Completions API → ответ пользователю,**

с нормальной обработкой ошибок, health-check'ом и минимальными тестами.

Работать итеративно:
- сам найдёшь все нужные файлы проекта,
- сам поправишь код,
- сам запустишь локальные проверки (по возможности),
- НЕ ОСТАНАВЛИВАЙСЯ на первой ошибке — правь до тех пор, пока:
  1) прямой запрос к OpenAI через backend проходит без ошибок,
  2) endpoint конвеера возвращает осмысленный ответ,
  3) бот при тестовом запросе отдаёт текст от модели (или понятное сообщение об ошибке).

---

## ТЕХНИЧЕСКИЕ УСЛОВИЯ

- Проект работает под Windows (пути вида `D:\projects\...`).
- Конвеер реализован в виде backend-сервиса (FastAPI / Python).
- Используем **официальный OpenAI API** (`https://api.openai.com/v1/chat/completions` или новый SDK).
- Ключ OpenAI берём **только из переменных окружения / конфигов**, в код его жёстко не вшивать.
- Текущий проект: Watson Agent 2.0
- Порт API: 8090
- Основной файл API: `api/fastapi_agent.py`

---

## ШАГ 1. ОБЗОР ПРОЕКТА

1. Просканируй репозиторий и найди:
   - backend/конвеер: `api/fastapi_agent.py`, `utils/router_core.py`
   - код Telegram-бота: `api/telegram_bot.py`, `scripts/telegram_bridge.py`
   - клиент LLM: `tools/llm_client.py`
   - общие настройки / конфиги: `config.toml`, `env.example`, `utils/profile_loader.py`

2. Составь внутреннюю карту:
   - endpoint конвеера: `/relay/submit` (уже есть в `api/fastapi_agent.py`)
   - где формируется запрос к LLM: `tools/llm_client.py`
   - где лежат настройки: `config.toml` + переменные окружения

---

## ШАГ 2. НОРМАЛЬНАЯ КОНФИГУРАЦИЯ OPENAI

Приведи конфигурацию OpenAI к одному, понятному месту.

### Текущее состояние:
- Используется LM Studio локально: `http://127.0.0.1:1234/v1`
- Модели: DeepSeek R1 + Qwen 2.5 Coder

### Требуется:
1. Добавить поддержку **настоящего OpenAI API** (`https://api.openai.com/v1`)
2. Создать/обновить модуль конфигурации:
   ```python
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
   OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
   OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
   ```

3. Добавить валидацию:
   - если `OPENAI_API_KEY` пустой при использовании OpenAI (не LM Studio) — понятная ошибка

---

## ШАГ 3. КЛИЕНТ ДЛЯ OPENAI (ЕДИНАЯ ТОЧКА ВХОДА)

Обнови существующий модуль `tools/llm_client.py`:

### Требования:

1. **Универсальный клиент:**
   - Работает и с LM Studio (`http://127.0.0.1:1234/v1`)
   - Работает и с OpenAI API (`https://api.openai.com/v1`)
   - Автоматически определяет по `base_url` какой провайдер используется

2. **Используй официальный OpenAI SDK:**
   ```python
   from openai import OpenAI
   
   client = OpenAI(
       api_key=api_key or "lm-studio",  # для LM Studio можно любой
       base_url=base_url
   )
   
   def chat(model, messages, temperature=0.2, max_tokens=2048):
       try:
           response = client.chat.completions.create(
               model=model,
               messages=messages,
               temperature=temperature,
               max_tokens=max_tokens
           )
           return response.choices[0].message.content
       except Exception as e:
           logger.error(f"LLM error: {e}")
           raise
   ```

3. **Обработка ошибок:**
   - Таймауты (timeout=120)
   - 401 (неверный ключ)
   - 429 (rate limits)
   - 5xx (ошибки провайдера)

4. **Логирование:**
   - Модель
   - Длину сообщений
   - Коды ошибок (БЕЗ полного ключа)

---

## ШАГ 4. ЭНДПОЙНТ КОНВЕЕРА (/relay/submit)

Endpoint УЖЕ СУЩЕСТВУЕТ в `api/fastapi_agent.py` (строки 303-438).

### Требуется:

1. **Проверить схему запроса:**
   ```python
   class RelaySubmitIn(BaseModel):
       text: str
       dry_run: bool = False
       chat_id: Optional[str] = None
   ```

2. **Убедиться, что используется правильный LLM клиент:**
   - Импорт: `from tools.llm_client import chat` или `LLMClient`
   - Вызов через нормализованный интерфейс

3. **Улучшить обработку intent "noncode":**
   - Сейчас возвращает захардкоденный текст
   - Нужно отправлять в LLM для диалога:
   ```python
   if intent == "noncode":
       # Отправить в OpenAI для обычного чата
       messages = [
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": body.text}
       ]
       reply = chat(model="gpt-4o-mini", messages=messages)
       return RelaySubmitOut(ok=True, intent="noncode", response=reply)
   ```

4. **Возвращать осмысленные ошибки:**
   ```python
   except Exception as e:
       logger.error(f"Relay error: {e}")
       return RelaySubmitOut(
           ok=False,
           intent="error",
           error=f"LLM service unavailable: {str(e)}"
       )
   ```

---

## ШАГ 5. HEALTH-CHECK ДЛЯ OPENAI

Добавь в `api/fastapi_agent.py` новый endpoint:

```python
@app.get("/health/openai")
def health_openai():
    """
    Проверка подключения к OpenAI API.
    Отправляет простой запрос и возвращает статус.
    """
    try:
        from tools.llm_client import chat
        
        messages = [{"role": "user", "content": "ping"}]
        response = chat(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=10
        )
        
        return {
            "status": "ok",
            "provider": "openai" if "openai.com" in os.getenv("OPENAI_BASE_URL", "") else "lm-studio",
            "llm_reply": response,
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        }
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "details": str(e),
                "suggestion": "Check OPENAI_API_KEY and OPENAI_BASE_URL environment variables"
            }
        )
```

---

## ШАГ 6. ИНТЕГРАЦИЯ С TELEGRAM-БОТОМ

### Найди:
- `api/telegram_bot.py` или `scripts/telegram_bridge.py`
- Handlers для сообщений

### Требуется:

1. **Убедиться, что бот использует `/relay/submit`:**
   ```python
   async def handle_message(message: Message):
       response = requests.post(
           "http://127.0.0.1:8090/relay/submit",
           json={
               "text": message.text,
               "chat_id": str(message.chat.id),
               "dry_run": False
           },
           timeout=60
       )
       
       if response.ok:
           data = response.json()
           await message.reply(data.get("response", "Нет ответа"))
       else:
           await message.reply(f"⚠️ Ошибка: {response.status_code}")
   ```

2. **Добавить команду `/ping` для диагностики:**
   ```python
   @dp.message_handler(commands=['ping'])
   async def cmd_ping(message: Message):
       try:
           # Проверка health
           health = requests.get("http://127.0.0.1:8090/health/openai", timeout=10)
           
           if health.ok:
               data = health.json()
               await message.reply(
                   f"✅ OpenAI: {data['status']}\n"
                   f"Provider: {data['provider']}\n"
                   f"Reply: {data['llm_reply']}"
               )
           else:
               await message.reply(f"❌ Health check failed: {health.status_code}")
       except Exception as e:
           await message.reply(f"⚠️ Ошибка связи: {e}")
   ```

---

## ШАГ 7. ТЕСТЫ / ПРОВЕРКА

Создай файл `tests/test_openai_integration.py`:

```python
import pytest
import os
from tools.llm_client import chat

def test_openai_client():
    """Тест прямого вызова OpenAI."""
    messages = [{"role": "user", "content": "Say 'test passed' if you can read this"}]
    response = chat(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        max_tokens=20
    )
    assert response is not None
    assert len(response) > 0

def test_health_openai():
    """Тест health-check endpoint."""
    import requests
    response = requests.get("http://127.0.0.1:8090/health/openai", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_relay_submit():
    """Тест endpoint /relay/submit."""
    import requests
    response = requests.post(
        "http://127.0.0.1:8090/relay/submit",
        json={"text": "ping", "dry_run": False},
        timeout=30
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "response" in data or "reply" in data
```

Запусти:
```bash
py -3.11 -m pytest tests/test_openai_integration.py -v
```

---

## ШАГ 8. ОБРАБОТКА ОШИБОК И ЛОГИРОВАНИЕ

Обеспечь в `tools/llm_client.py`:

```python
import logging

logger = logging.getLogger(__name__)

def chat(model, messages, **kwargs):
    try:
        logger.info(f"LLM request: model={model}, messages_count={len(messages)}")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        reply = response.choices[0].message.content
        logger.info(f"LLM response: {len(reply)} chars")
        
        return reply
        
    except openai.AuthenticationError as e:
        logger.error(f"Authentication error: Check OPENAI_API_KEY")
        raise
    except openai.RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        raise
    except openai.APITimeoutError as e:
        logger.error(f"Request timeout: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected LLM error: {e}")
        raise
```

**Важно:**
- НЕ логировать API ключ
- НЕ логировать полный текст сообщений (только длину)
- Логировать коды ошибок и типы исключений

---

## ШАГ 9. НЕ ОСТАНАВЛИВАТЬСЯ, ПОКА НЕ РАБОТАЕТ

Продолжай работу, пока не выполнятся ВСЕ условия:

### ✅ Checklist:

- [ ] `tools/llm_client.py` поддерживает OpenAI API
- [ ] `tools/llm_client.py` поддерживает LM Studio (backward compatibility)
- [ ] Endpoint `/health/openai` возвращает 200 OK
- [ ] Endpoint `/relay/submit` обрабатывает noncode запросы через LLM
- [ ] Telegram бот отправляет запросы в `/relay/submit`
- [ ] Команда `/ping` работает и показывает статус
- [ ] Тесты проходят (хотя бы 2 из 3)
- [ ] Все ошибки логируются правильно
- [ ] API ключ не попадает в логи/ответы
- [ ] `env.example` обновлён с OpenAI настройками

### Тестирование:

```powershell
# 1. Проверка health
curl http://127.0.0.1:8090/health/openai

# 2. Проверка relay
$body = @{ text = "Hello, can you hear me?" } | ConvertTo-Json
curl -X POST http://127.0.0.1:8090/relay/submit `
  -H "Content-Type: application/json" -d $body

# 3. Проверка Telegram (отправить сообщение боту)
# Должен ответить осмысленным текстом от LLM
```

---

## ШАГ 10. ФИНАЛЬНАЯ ДОКУМЕНТАЦИЯ

Создай файл `OPENAI_INTEGRATION.md` с описанием:

### Содержание:

1. **Настройка переменных окружения:**
   ```powershell
   $env:OPENAI_API_KEY = "sk-..."
   $env:OPENAI_BASE_URL = "https://api.openai.com/v1"
   $env:OPENAI_MODEL = "gpt-4o-mini"
   ```

2. **Запуск backend:**
   ```powershell
   pwsh scripts/Start-WatsonApi.ps1 -Port 8090
   ```

3. **Проверка работы:**
   - Health: `curl http://127.0.0.1:8090/health/openai`
   - Relay: см. примеры выше
   - Telegram: отправить сообщение боту

4. **Troubleshooting:**
   - 401 Unauthorized → проверь OPENAI_API_KEY
   - 503 Service Unavailable → LLM недоступен
   - Connection timeout → проверь OPENAI_BASE_URL

5. **Переключение между LM Studio и OpenAI:**
   ```powershell
   # LM Studio (локально)
   $env:OPENAI_BASE_URL = "http://127.0.0.1:1234/v1"
   $env:OPENAI_API_KEY = "lm-studio"
   
   # OpenAI (облако)
   $env:OPENAI_BASE_URL = "https://api.openai.com/v1"
   $env:OPENAI_API_KEY = "sk-..."
   ```

---

## ИТОГОВЫЙ РЕЗУЛЬТАТ

После выполнения всех шагов должно работать:

1. ✅ Telegram бот принимает сообщения
2. ✅ Бот отправляет запрос в `/relay/submit`
3. ✅ Конвеер определяет intent (code/noncode/help/etc)
4. ✅ Для noncode - отправляет в OpenAI Chat API
5. ✅ Получает ответ от GPT-4o-mini (или другой модели)
6. ✅ Возвращает ответ пользователю в Telegram
7. ✅ Все ошибки логируются и обрабатываются
8. ✅ Health-check показывает статус OpenAI

---

## АВТОМАТИЗАЦИЯ (БОНУС)

Если есть время, добавь:

1. **Retry механизм:**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
   def chat_with_retry(model, messages, **kwargs):
       return chat(model, messages, **kwargs)
   ```

2. **Кэширование простых запросов:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_simple_reply(text: str) -> str:
       # Для FAQ и простых вопросов
       pass
   ```

3. **Мониторинг usage:**
   ```python
   def log_usage(response):
       usage = response.usage
       logger.info(f"Tokens: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
   ```

---

## ⚡ НАЧНИ РАБОТУ ПРЯМО СЕЙЧАС

Cursor, ты видишь этот файл. Начинай выполнение по шагам с 1 по 10.

**Не останавливайся, пока все чекбоксы в ШАГ 9 не будут отмечены!**

Если встречаешь ошибку - анализируй, исправляй, тестируй снова.

Удачи! 🚀

---

**"Лучший код - это код, который написал кто-то другой, пока ты пьёшь кофе."** ☕

