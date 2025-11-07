# utils/nlp_router.py
import os, json
from urllib.request import Request, urlopen
from urllib.error import URLError
from typing import Optional, Tuple

LM_BASE = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
LM_KEY  = os.getenv("OPENAI_API_KEY", "lm-studio")
PLANNER = os.getenv("WATSON_PLANNER_MODEL", "deepseek-r1-distill-qwen-14b-abliterated-v2")

SYSTEM = (
  "Ты — маршрутизатор задач для автокодера. "
  "Получаешь текст от пользователя (любой простоты/языка) и возвращаешь СТРОГИЙ JSON без лишнего текста.\n"
  "Формат JSON:\n"
  "{"
  "  \"intent\": \"code|noncode|help|ping|project_create\","
  "  \"task\": \"краткая формулировка для автокодера (англ или рус)\","
  "  \"project_name\": \"<для project_create: краткое имя латиницей>\","
  "  \"files\": [\"relative/path1\", \"relative/path2\"],"
  "  \"acceptance\": [\"критерий 1\", \"критерий 2\"],"
  "  \"notes\": \"опциональные уточнения\","
  "  \"dry_run\": false"
  "}\n"
  "Правила:\n"
  "- Приветствия/общение → intent=noncode.\n"
  "- «Проверь / ответь / получил?» → help или ping.\n"
  "- Создание НОВОГО проекта («создай проект», «create project») → intent=project_create, project_name (латиница без пробелов).\n"
  "- Любое кодовое улучшение (add/refactor/fix/tests) → intent=code, task коротко (imperative), files по возможности relative.\n"
  "- Без markdown, без комментариев — только валидный JSON."
)

def _chat(prompt: str) -> str:
    body = json.dumps({
        "model": PLANNER,
        "messages": [{"role":"system","content":SYSTEM},
                     {"role":"user","content":prompt}],
        "temperature": 0.2,
        "max_tokens": 600
    }).encode("utf-8")
    req = Request(f"{LM_BASE}/chat/completions", data=body,
                  headers={"Content-Type":"application/json","Authorization":f"Bearer {LM_KEY}"})
    with urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()

def normalize(text: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Возвращает (payload, error). payload — словарь в описанном формате.
    Fallback: если LLM недоступен, возвращаем базовый code intent.
    """
    try:
        raw = _chat(text)
        # иногда модели оборачивают в ```json ... ```
        if raw.startswith("```"):
            raw = raw.strip("` \n")
            if raw.startswith("json"): raw = raw[4:].strip()
        payload = json.loads(raw)
        # sanity checks
        if "intent" not in payload:
            return None, "router: missing intent"
        if payload.get("intent") == "code" and not payload.get("task"):
            return None, "router: empty coding task"
        return payload, None
    except URLError as e:
        # Fallback: если LM Studio недоступен, используем текст как есть
        return _fallback_normalize(text), None
    except Exception as e:
        # Fallback: если парсинг JSON не удался, используем текст как есть
        return _fallback_normalize(text), None

def _fallback_normalize(text: str) -> dict:
    """
    Простой fallback когда DeepSeek-R1 недоступен.
    Проверяет базовые ключевые слова и возвращает intent.
    """
    text_lower = text.lower()
    
    # Проверка на команды
    if any(cmd in text_lower for cmd in ['/ping', 'ping', 'понг', 'pong']):
        return {"intent": "ping", "task": "", "project_name": "", "files": [], "acceptance": [], "notes": "", "dry_run": False}
    
    if any(cmd in text_lower for cmd in ['/help', 'help', 'помощ', 'справк']):
        return {"intent": "help", "task": "", "project_name": "", "files": [], "acceptance": [], "notes": "", "dry_run": False}
    
    # Проверка на создание проекта
    project_keywords = ['создай проект', 'создать проект', 'create project', 'new project', 'создай прое']
    if any(kw in text_lower for kw in project_keywords):
        # Извлекаем название (всё после ключевого слова)
        for kw in project_keywords:
            if kw in text_lower:
                name_part = text[text_lower.index(kw) + len(kw):].strip(' "\'')
                return {
                    "intent": "project_create",
                    "task": "",
                    "project_name": name_part or "new_project",
                    "files": [],
                    "acceptance": [],
                    "notes": f"fallback extraction from: {text}",
                    "dry_run": False
                }
    
    # Проверка на приветствия/общение
    if any(greet in text_lower for greet in ['привет', 'hello', 'здравств', 'как дела', 'ответь']):
        return {"intent": "noncode", "task": "", "project_name": "", "files": [], "acceptance": [], "notes": "", "dry_run": False}
    
    # Проверка на кодовые ключевые слова
    coding_keywords = ['add', 'fix', 'refactor', 'test', 'implement', 'update', 'remove', 'change',
                      'добав', 'исправ', 'измен', 'удал', 'рефактор', 'лог', 'сдела', 'напиш',
                      'улучш', 'оптимиз', 'почин', 'поправ', 'внедри', 'интегр']
    if any(kw in text_lower for kw in coding_keywords):
        return {
            "intent": "code",
            "task": text,
            "project_name": "",
            "files": [],
            "acceptance": [],
            "notes": "fallback: DeepSeek-R1 unavailable",
            "dry_run": False
        }
    
    # По умолчанию — noncode
    return {"intent": "noncode", "task": "", "project_name": "", "files": [], "acceptance": [], "notes": "", "dry_run": False}

