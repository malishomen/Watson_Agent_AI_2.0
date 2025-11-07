# AI Agent API - FastAPI СЃРµСЂРІРµСЂ РґР»СЏ Р°РІС‚РѕРЅРѕРјРЅРѕРіРѕ Р°РіРµРЅС‚Р°
# РРЅС‚РµРіСЂР°С†РёСЏ СЃ LM Studio Рё Р°РІС‚РѕРјР°С‚РёР·Р°С†РёСЏ Cursor

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
from typing import Optional, Dict, Any

app = FastAPI(
    title="AI Agent API",
    description="РђРІС‚РѕРЅРѕРјРЅС‹Р№ AI-Р°РіРµРЅС‚ РґР»СЏ СЂР°Р·СЂР°Р±РѕС‚РєРё СЃ Cursor",
    version="1.0.0"
)

# РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ
LM_STUDIO_URL = "http://127.0.0.1:1234"
API_SECRET = "test123"

class TaskRequest(BaseModel):
    task: str
    project_path: str = "D:\\AI-Agent\\fresh_start"
    timeout: int = 300

class TaskResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    lm_studio: bool
    cursor_available: bool

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """РџСЂРѕРІРµСЂРєР° СЃРѕСЃС‚РѕСЏРЅРёСЏ СЃРёСЃС‚РµРјС‹"""
    try:
        # РџСЂРѕРІРµСЂРєР° LM Studio
        lm_response = requests.get(f"{LM_STUDIO_URL}/v1/models", timeout=5)
        lm_studio_ok = lm_response.status_code == 200
    except:
        lm_studio_ok = False
    
    try:
        # РџСЂРѕРІРµСЂРєР° Cursor
        cursor_available = os.system("cursor --version >nul 2>&1") == 0
    except:
        cursor_available = False
    
    return HealthResponse(
        status="ok" if lm_studio_ok and cursor_available else "degraded",
        lm_studio=lm_studio_ok,
        cursor_available=cursor_available
    )

@app.post("/task", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """РЎРѕР·РґР°РЅРёРµ РЅРѕРІРѕР№ Р·Р°РґР°С‡Рё РґР»СЏ Р°РіРµРЅС‚Р°"""
    try:
        # Р“РµРЅРµСЂР°С†РёСЏ ID Р·Р°РґР°С‡Рё
        task_id = f"task_{hash(request.task) % 10000:04d}"
        
        # РЎРѕС…СЂР°РЅРµРЅРёРµ Р·Р°РґР°С‡Рё РІ С„Р°Р№Р»
        task_file = f"tasks/{task_id}.json"
        os.makedirs("tasks", exist_ok=True)
        
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump({
                "task": request.task,
                "project_path": request.project_path,
                "timeout": request.timeout,
                "status": "pending"
            }, f, ensure_ascii=False, indent=2)
        
        return TaskResponse(
            status="created",
            message=f"Task created: {request.task}",
            task_id=task_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}")
async def get_task(task_id: str):
    """РџРѕР»СѓС‡РµРЅРёРµ СЃС‚Р°С‚СѓСЃР° Р·Р°РґР°С‡Рё"""
    task_file = f"tasks/{task_id}.json"
    
    if not os.path.exists(task_file):
        raise HTTPException(status_code=404, detail="Task not found")
    
    with open(task_file, "r", encoding="utf-8") as f:
        task_data = json.load(f)
    
    return task_data

@app.post("/cursor/terminal")
async def cursor_terminal(command: Dict[str, str]):
    """Р’С‹РїРѕР»РЅРµРЅРёРµ РєРѕРјР°РЅРґС‹ РІ С‚РµСЂРјРёРЅР°Р»Рµ Cursor"""
    try:
        cwd = command.get("cwd", "D:\\AI-Agent\\fresh_start")
        cmd = command.get("command", "")
        
        # Р—РґРµСЃСЊ Р±СѓРґРµС‚ РёРЅС‚РµРіСЂР°С†РёСЏ СЃ Cursor С‡РµСЂРµР· pyautogui
        # РџРѕРєР° РІРѕР·РІСЂР°С‰Р°РµРј СѓСЃРїРµС…
        return {
            "status": "success",
            "command": cmd,
            "cwd": cwd,
            "output": "Command executed in Cursor terminal"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cursor/agent")
async def cursor_agent(task: Dict[str, str]):
    """РћС‚РїСЂР°РІРєР° Р·Р°РґР°С‡Рё РІ Cursor Agent"""
    try:
        task_text = task.get("task", "")
        
        # Р—РґРµСЃСЊ Р±СѓРґРµС‚ РёРЅС‚РµРіСЂР°С†РёСЏ СЃ Cursor Agent Mode
        # РџРѕРєР° РІРѕР·РІСЂР°С‰Р°РµРј СѓСЃРїРµС…
        return {
            "status": "success",
            "task": task_text,
            "message": "Task sent to Cursor Agent"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8088)





