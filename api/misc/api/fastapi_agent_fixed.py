# -*- coding: utf-8 -*-
import os, sys, traceback, json, sqlite3, yaml
from fastapi import FastAPI, Header, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List

# РіР°СЂР°РЅС‚РёСЂСѓРµРј, С‡С‚Рѕ РїСЂРѕРµРєС‚РЅС‹Р№ РєРѕСЂРµРЅСЊ РІ sys.path (С‡С‚РѕР±С‹ РЅРµ РїР°РґР°Р»Рё РёРјРїРѕСЂС‚С‹)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Р’РђР–РќРћ: РёРјРїРѕСЂС‚РёСЂСѓРµРј Р·РґРµСЃСЊ вЂ” РµСЃР»Рё Р±СѓРґРµС‚ РѕС€РёР±РєР°, СѓРІРёРґРёРј РїРѕР»РЅСѓСЋ С‚СЂР°СЃСЃРёСЂРѕРІРєСѓ
from api.parsers.nlp_command_router import parse_free_text
import importlib.util
spec = importlib.util.spec_from_file_location("agent", "Memory/GPT+Deepseek_Agent_memory.py")
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
init_db = agent_module.init_db
get_or_create_session = agent_module.get_or_create_session
respond = agent_module.respond

app = FastAPI()

# --- РџСЂРѕСЃС‚РѕР№ middleware (РіР°СЂР°РЅС‚РёСЏ UTF-8 Рё Р±Р°Р·РѕРІС‹Р№ CORS РїСЂРё РЅР°РґРѕР±РЅРѕСЃС‚Рё) ---
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class Utf8Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # РїСЂРёРЅСѓРґРёС‚РµР»СЊРЅРѕ СЃС‡РёС‚Р°РµРј С‚РµР»Рѕ РєР°Рє UTF-8; FastAPI СЃР°Рј СЂР°Р·Р±РµСЂС‘С‚ JSON
        response = await call_next(request)
        # Р“Р°СЂР°РЅС‚РёСЂСѓРµРј РєРѕСЂСЂРµРєС‚РЅС‹Р№ header РґР»СЏ РєР»РёРµРЅС‚РѕРІ (РІ С‚.С‡. PowerShell)
        if "application/json" in response.headers.get("content-type", ""):
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

app.add_middleware(Utf8Middleware)

def verify_secret(x_agent_secret: str = Header(...)):
    expected = (os.getenv("AGENT_HTTP_SHARED_SECRET") or "").strip()
    got = (x_agent_secret or "").strip()
    if not expected or got != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class CommandIn(BaseModel):
    text: str = Field(default="")
    session: Optional[str] = Field(default="Telegram")
    mode: Optional[str] = None

class CommandOut(BaseModel):
    ok: bool
    normalized: str
    result: str

class ApprovalItem(BaseModel):
    id: str
    action: str
    params: dict
    status: str
    created_at: str
    resolved_at: str | None = None

class ProjectSpecIn(BaseModel):
    spec_text: Optional[str] = None
    spec_path: Optional[str] = None
    session: Optional[str] = "Project"

class ProjectRunIn(BaseModel):
    project_id: str
    session: Optional[str] = "Project"
    resume: bool = True

class ProjectStatusOut(BaseModel):
    project_id: str
    state: str
    current_step: int
    total_steps: int
    last_message: str
    errors: List[str]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/command", response_model=CommandOut)
def command_endpoint(payload: CommandIn, _=Depends(verify_secret)):
    try:
        init_db()
        sid = get_or_create_session(payload.session or "Telegram")
        raw = payload.text or ""
        normalized = raw if raw.strip().startswith("/") else parse_free_text(raw)
        result = respond(sid, normalized)
        # РЎС‚СЂР°С…СѓРµРјСЃСЏ: СЂРµР·СѓР»СЊС‚Р°С‚ С‚РѕР¶Рµ РІ UTF-8
        if isinstance(result, bytes):
            result = result.decode("utf-8", errors="replace")
        return CommandOut(ok=True, normalized=normalized, result=result)
    except Exception as e:
        tb = traceback.format_exc()
        print("[/command ERROR]\n", tb, flush=True)  # РІРёРґРЅРѕ РІ РєРѕРЅСЃРѕР»Рё uvicorn
        return CommandOut(ok=False, normalized=payload.text or "", result=f"РћС€РёР±РєР°: {e}")

def _db_path():
    # РїСѓС‚СЊ Рє Р±Р°Р·Рµ РґР°РЅРЅС‹С… Р°РіРµРЅС‚Р°
    return os.path.join(os.path.dirname(__file__), "..", "Memory", "agent_memory.sqlite")

@app.get("/approvals/pending", response_model=List[ApprovalItem], dependencies=[Depends(verify_secret)])
def approvals_pending():
    try:
        con = sqlite3.connect(_db_path())
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT id, action, params, status, created_at, resolved_at "
            "FROM approvals WHERE status='pending' ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        con.close()
        out = []
        for r in rows:
            out.append(ApprovalItem(
                id=r["id"],
                action=r["action"],
                params=json.loads(r["params"] or "{}"),
                status=r["status"],
                created_at=r["created_at"],
                resolved_at=r["resolved_at"],
            ))
        return out
    except Exception as e:
        print(f"[/approvals/pending ERROR] {e}", flush=True)
        return []

@app.post("/project/validate")
def project_validate(payload: ProjectSpecIn, _=Depends(verify_secret)):
    try:
        text = payload.spec_text
        if not text and payload.spec_path:
            with open(payload.spec_path, "r", encoding="utf-8") as f:
                text = f.read()
        if not text:
            raise ValueError("spec_text or spec_path required")
        spec = yaml.safe_load(text)
        # Р±Р°Р·РѕРІС‹Рµ РїСЂРѕРІРµСЂРєРё
        assert "name" in spec and "steps" in spec and isinstance(spec["steps"], list)
        return {"ok": True, "project_id": spec.get("name"), "steps": len(spec["steps"])}
    except Exception as e:
        return {"ok": False, "error": f"{e}"}

@app.post("/project/upload")
def project_upload(file: UploadFile = File(...), _=Depends(verify_secret)):
    try:
        content = file.file.read().decode("utf-8")
        spec = yaml.safe_load(content)
        pid = spec.get("name") or "project"
        dst = f"D:/AI-Agent/Projects/{pid}/ProjectSpec.yml"
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "project_id": pid, "spec_path": dst}
    except Exception as e:
        return {"ok": False, "error": f"{e}"}

@app.post("/project/run")
def project_run(payload: ProjectRunIn, _=Depends(verify_secret)):
    try:
        from orchestrator.project_runner import run_project
        result = run_project(payload.project_id, resume=payload.resume, session=payload.session or "Project")
        return {"ok": True, "result": result}
    except Exception as e:
        print("[/project/run ERROR]\n", traceback.format_exc(), flush=True)
        return {"ok": False, "error": f"{e}"}

@app.get("/project/status", response_model=ProjectStatusOut)
def project_status(project_id: str, _=Depends(verify_secret)):
    try:
        from orchestrator.project_state import load_state
        st = load_state(project_id)
        return ProjectStatusOut(
            project_id=project_id,
            state=st.get("state", "unknown"),
            current_step=st.get("current_step", 0),
            total_steps=st.get("total_steps", 0),
            last_message=st.get("last_message", ""),
            errors=st.get("errors", []),
        )
    except Exception as e:
        print(f"[/project/status ERROR] {e}", flush=True)
        return ProjectStatusOut(
            project_id=project_id,
            state="error",
            current_step=0,
            total_steps=0,
            last_message=f"Error: {e}",
            errors=[str(e)]
        )
