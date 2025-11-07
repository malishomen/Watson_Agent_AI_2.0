# parsers/nlp_command_router.py
# РџСЂРѕСЃС‚РѕР№ РіРёР±СЂРёРґРЅС‹Р№ РїР°СЂСЃРµСЂ: RU/EN в†’ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Рµ РєРѕРјР°РЅРґС‹ Р°РіРµРЅС‚Р°/С‚РµСЂРјРёРЅР°Р»Р°.
import re
from pathlib import Path

# Р±С‹СЃС‚СЂС‹Рµ СЃР»РѕРІР°СЂРё СЃРёРЅРѕРЅРёРјРѕРІ
RUN_WORDS = r"(Р·Р°РїСѓСЃС‚Рё|Р·Р°РїСѓСЃРє|РѕС‚РєСЂРѕР№|run|start|launch)"
READ_WORDS = r"(РїСЂРѕС‡РёС‚Р°Р№|РїСЂРѕС‡РёС‚Р°С‚СЊ|read|show\s+file|cat|type)"
WRITE_WORDS = r"(Р·Р°РїРёС€Рё|Р·Р°РїРёСЃР°С‚СЊ|РґРѕР±Р°РІСЊ|write|append)"
KILL_WORDS = r"(СѓР±РµР№|РѕСЃС‚Р°РЅРѕРІРё|kill|terminate|stop\s+process)"
PWD_WORDS = r"(РіРґРµ\s+СЏ|СЂР°Р±РѕС‡Р°СЏ\s+РґРёСЂРµРєС‚РѕСЂРёСЏ|pwd|where\s+am\s+i)"
CD_WORDS  = r"(РїРµСЂРµР№РґРё\s+РІ|СЃРјРµРЅРёС‚СЊ\s+РґРёСЂРµРєС‚РѕСЂРёСЋ|cd|chdir)"
PROC_LIST = r"(РїРѕРєР°Р¶Рё\s+РїСЂРѕС†РµСЃСЃС‹|СЃРїРёСЃРѕРє\s+РїСЂРѕС†РµСЃСЃРѕРІ|tasklist|process\s+list)"
GPU_TEMP  = r"(С‚РµРјРїРµСЂР°С‚СѓСЂСѓ\s+gpu|gpu\s*temp|gpu\s*temperature)"

# Project commands
PROJECT_RUN = r"(Р·Р°РїСѓСЃС‚Рё\s+РїСЂРѕРµРєС‚|start\s+project|run\s+project)"
PROJECT_STATUS = r"(СЃС‚Р°С‚СѓСЃ\s+РїСЂРѕРµРєС‚Р°|project\s+status|СЃС‚Р°С‚СѓСЃ\s+РїСЂРѕРµРєС‚Р°)"
PROJECT_LIST = r"(СЃРїРёСЃРѕРє\s+РїСЂРѕРµРєС‚РѕРІ|list\s+projects|РїСЂРѕРµРєС‚С‹)"

def _quote(path: str) -> str:
    if not path:
        return path
    p = path.strip()
    if " " in p and not (p.startswith('"') and p.endswith('"')):
        return f'"{p}"'
    return p

def parse_free_text(text: str) -> str:
    """
    Р’РѕР·РІСЂР°С‰Р°РµС‚ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅСѓСЋ РєРѕРјР°РЅРґСѓ РґР»СЏ Р°РіРµРЅС‚Р°:
    - /run "exe" [args]
    - /read D:\file.txt
    - /write D:\file.txt ::: TEXT
    - /kill notepad.exe | /kill 1234
    - /cd D:\workdir
    - /pwd
    - /cursor/terminal <command>  (РєР°Рє backoff)
    Р•СЃР»Рё С‚РµРєСЃС‚ СѓР¶Рµ РЅР°С‡РёРЅР°РµС‚СЃСЏ СЃ '/', РІРѕР·РІСЂР°С‰Р°РµРј РєР°Рє РµСЃС‚СЊ.
    """
    if not text:
        return "/pwd"

    t = text.strip()
    low = t.lower()

    # РЈР¶Рµ РЅРѕСЂРјР°Р»СЊРЅР°СЏ РєРѕРјР°РЅРґР°?
    if low.startswith("/"):
        return t

    # 1) РїСЂРѕС†РµСЃСЃС‹
    if re.search(PROC_LIST, low):
        return '/cursor/terminal tasklist'

    # 2) GPU С‚РµРјРїРµСЂР°С‚СѓСЂР° (РїСЂРёРјРµСЂ СЃРІРѕР±РѕРґРЅРѕРіРѕ РЅР°РІС‹РєР° в†’ С‚РµСЂРјРёРЅР°Р»)
    if re.search(GPU_TEMP, low):
        # nvidia-smi Сѓ NVIDIA; РїРѕРґ AMD Р°РґР°РїС‚РёСЂРѕРІР°С‚СЊ (radeon-profile-cli Рё С‚.Рї.)
        return '/cursor/terminal nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'

    # 3) run
    if re.search(RUN_WORDS, low):
        # СЌРІСЂРёСЃС‚РёРєР°: РІС‹С‚Р°С‰РёРј СЃР»РѕРІРѕ РїРѕСЃР»Рµ РіР»Р°РіРѕР»Р°
        m = re.search(r"(?:Р·Р°РїСѓСЃС‚Рё|Р·Р°РїСѓСЃРє|РѕС‚РєСЂРѕР№|run|start|launch)\s+(.+)$", low)
        if m:
            payload = m.group(1).strip()
            # РµСЃР»Рё РїСѓС‚СЊ .exe РёР»Рё .bat/.cmd
            if re.search(r"\.(exe|bat|cmd|ps1)\b", payload):
                return f'/run {_quote(payload)}'
            # РёРЅР°С‡Рµ РїРѕРїСЂРѕР±СѓРµРј РєР°Рє РёРјСЏ РїСЂРѕРіСЂР°РјРјС‹
            return f'/run "{payload}"'
        return '/run "notepad.exe"'

    # 4) read
    if re.search(READ_WORDS, low):
        # РёР·РІР»РµС‡СЊ РїСѓС‚СЊ (РЅР°РёРІРЅРѕ)
        m = re.search(r"([a-z]:\\[^<>:\"|?*]+)", t, re.IGNORECASE)
        if m:
            return f"/read {m.group(1)}"
        return "/read D:\\AI-Agent\\README.md"

    # 5) write
    if re.search(WRITE_WORDS, low):
        # С„РѕСЂРјР°С‚: "Р·Р°РїРёС€Рё РІ D:\file.txt: С‚РµРєСЃС‚ ..."
        m = re.search(r"РІ\s+([a-z]:\\[^<>:\"|?*]+)\s*[:\-вЂ”]\s*(.+)$", t, re.IGNORECASE)
        if m:
            path, body = m.group(1).strip(), m.group(2).strip()
            return f"/write {path} ::: {body}"
        # Р·Р°РїР°СЃРЅРѕР№ РІР°СЂРёР°РЅС‚
        return '/write D:\\AI-Agent\\notes.txt ::: Р”РѕР±Р°РІР»РµРЅРѕ РёР· СЃРІРѕР±РѕРґРЅРѕР№ РєРѕРјР°РЅРґС‹'

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

    # 9) project commands
    if re.search(PROJECT_RUN, low):
        # "Р·Р°РїСѓСЃС‚Рё РїСЂРѕРµРєС‚ demo" в†’ "/project.run demo"
        m = re.search(PROJECT_RUN + r"\s+(\w+)$", low)
        if m:
            return f"/project.run {m.group(1)}"
        return "/project.run demo"

    if re.search(PROJECT_STATUS, low):
        # "СЃС‚Р°С‚СѓСЃ РїСЂРѕРµРєС‚Р° demo" в†’ "/project.status demo"
        m = re.search(PROJECT_STATUS + r"\s+(\w+)$", low)
        if m:
            return f"/project.status {m.group(1)}"
        return "/project.status demo"

    if re.search(PROJECT_LIST, low):
        # "СЃРїРёСЃРѕРє РїСЂРѕРµРєС‚РѕРІ" в†’ "/project.list"
        return "/project.list"

    # 10) fallback в†’ С‚РµСЂРјРёРЅР°Р» РёР»Рё РґРёР°Р»РѕРі LLM
    # РЎРЅР°С‡Р°Р»Р° РїРѕРїСЂРѕР±СѓРµРј С‚РµСЂРјРёРЅР°Р» "РєР°Рє РµСЃС‚СЊ" (РѕСЃС‚РѕСЂРѕР¶РЅРѕ!)
    # РњРѕР¶РЅРѕ РІРєР»СЋС‡Р°С‚СЊ С‚РѕР»СЊРєРѕ РїРѕ РєР»СЋС‡РµРІРѕРјСѓ СЃР»РѕРІСѓ, РЅРѕ РґР»СЏ РґРµРјРѕРЅСЃС‚СЂР°С†РёРё РѕСЃС‚Р°РІРёРј С‚Р°Рє:
    if low.startswith("С‚РµСЂРјРёРЅР°Р» ") or low.startswith("terminal "):
        cmd = t.split(" ", 1)[1]
        return f"/cursor/terminal {cmd}"

    # РРЅР°С‡Рµ РѕС‚РґР°С‘Рј РЅР° РѕР±С‹С‡РЅС‹Р№ Р°РіРµРЅС‚РЅС‹Р№ РґРёР°Р»РѕРі (LLM)
    return t  # РїСѓСЃС‚СЊ respond РѕР±СЂР°Р±РѕС‚Р°РµС‚ РєР°Рє РѕР±С‹С‡РЅС‹Р№ С‡Р°С‚
