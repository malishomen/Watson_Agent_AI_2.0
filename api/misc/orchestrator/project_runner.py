# -*- coding: utf-8 -*-
"""
Project Runner - Р’С‹РїРѕР»РЅРµРЅРёРµ РїСЂРѕРµРєС‚РѕРІ РїРѕ СЃРїРµС†РёС„РёРєР°С†РёРё
"""
import os, yaml, json, subprocess, shlex, time
from pathlib import Path
from .project_state import load_state, save_state

BASE = "D:/AI-Agent/Projects"
WHITELIST = [
    Path("D:/AI-Agent").resolve(), 
    Path("D:/Projects").resolve(), 
    Path("D:/Temp").resolve()
]

def _spec_path(pid):
    """РџСѓС‚СЊ Рє С„Р°Р№Р»Сѓ СЃРїРµС†РёС„РёРєР°С†РёРё РїСЂРѕРµРєС‚Р°"""
    return os.path.join(BASE, pid, "ProjectSpec.yml")

def _shell(cmd, cwd=None, timeout=600):
    """Р’С‹РїРѕР»РЅРµРЅРёРµ shell РєРѕРјР°РЅРґС‹"""
    proc = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True, 
        cwd=cwd, 
        timeout=timeout,
        encoding="utf-8"
    )
    out = (proc.stdout or "") + (("\nERR:\n" + proc.stderr) if proc.stderr else "")
    return proc.returncode, out.strip()

def _check_whitelist(path):
    """РџСЂРѕРІРµСЂРєР°, С‡С‚Рѕ РїСѓС‚СЊ РІ Р±РµР»РѕРј СЃРїРёСЃРєРµ"""
    try:
        abs_path = Path(path).resolve()
        return any(abs_path.is_relative_to(wl) for wl in WHITELIST)
    except:
        return False

def _write_file_safe(path, content):
    """Р‘РµР·РѕРїР°СЃРЅР°СЏ Р·Р°РїРёСЃСЊ С„Р°Р№Р»Р° СЃ РїСЂРѕРІРµСЂРєРѕР№ Р±РµР»РѕРіРѕ СЃРїРёСЃРєР°"""
    if not _check_whitelist(path):
        raise ValueError(f"Path {path} is not in whitelist")
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {path}"

def _read_file_safe(path):
    """Р‘РµР·РѕРїР°СЃРЅРѕРµ С‡С‚РµРЅРёРµ С„Р°Р№Р»Р° СЃ РїСЂРѕРІРµСЂРєРѕР№ Р±РµР»РѕРіРѕ СЃРїРёСЃРєР°"""
    if not _check_whitelist(path):
        raise ValueError(f"Path {path} is not in whitelist")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def run_step(pid, step, state):
    """Р’С‹РїРѕР»РЅРµРЅРёРµ РѕРґРЅРѕРіРѕ С€Р°РіР° РїСЂРѕРµРєС‚Р°"""
    step_type = step.get("type")
    msg = ""
    
    try:
        if step_type == "file.write":
            path, text = step["path"], step["text"]
            msg = _write_file_safe(path, text)
            
        elif step_type == "file.append":
            path, text = step["path"], step["text"]
            old = ""
            try:
                old = _read_file_safe(path)
            except:
                pass
            new_content = old + ("\n" if old and not old.endswith("\n") else "") + text
            msg = _write_file_safe(path, new_content)
            
        elif step_type == "shell":
            cmd = step["command"]
            cwd = step.get("cwd")
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            code, out = _shell(cmd, cwd=cwd)
            msg = f"(code={code})\n{out}"
            if code != 0:
                raise RuntimeError(f"Shell failed: {cmd}")
                
        elif step_type == "git.init":
            cwd = step.get("cwd")
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            code, out = _shell("git init", cwd=cwd)
            msg = out
            
        elif step_type == "git.commit":
            cwd = step.get("cwd")
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            message = step.get("message", "init")
            code, out = _shell(f'git add . && git commit -m "{message}"', cwd=cwd)
            msg = out
            
        elif step_type == "python.run":
            script = step["script"]
            args = step.get("args", "")
            cwd = step.get("cwd")
            
            if not _check_whitelist(script):
                raise ValueError(f"Script {script} is not in whitelist")
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            code, out = _shell(f'python "{script}" {args}', cwd=cwd)
            msg = out
            if code != 0:
                raise RuntimeError(f"Python failed: {script}")
                
        elif step_type == "docker.build":
            tag = step["tag"]
            context = step.get("context", ".")
            cwd = step.get("cwd")
            
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            code, out = _shell(f'docker build -t {tag} {context}', cwd=cwd)
            msg = out
            if code != 0:
                raise RuntimeError("Docker build failed")
                
        elif step_type == "docker.run":
            tag = step["tag"]
            args = step.get("args", "")
            cwd = step.get("cwd")
            
            if cwd and not _check_whitelist(cwd):
                raise ValueError(f"Working directory {cwd} is not in whitelist")
            
            code, out = _shell(f'docker run --rm {args} {tag}', cwd=cwd)
            msg = out
            if code != 0:
                raise RuntimeError("Docker run failed")
                
        elif step_type == "wait":
            seconds = step.get("seconds", 1)
            time.sleep(seconds)
            msg = f"Waited {seconds} seconds"
            
        else:
            msg = f"Unknown step type: {step_type}"
            
    except Exception as e:
        raise RuntimeError(f"Step execution failed: {e}")
    
    state["last_message"] = msg
    return msg

def run_project(pid, resume=True, session="Project"):
    """Р—Р°РїСѓСЃРє РїСЂРѕРµРєС‚Р° РїРѕ СЃРїРµС†РёС„РёРєР°С†РёРё"""
    try:
        # Р—Р°РіСЂСѓР¶Р°РµРј СЃРїРµС†РёС„РёРєР°С†РёСЋ
        spec_path = _spec_path(pid)
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Project spec not found: {spec_path}")
            
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        
        steps = spec.get("steps", [])
        if not steps:
            raise ValueError("No steps defined in project spec")
        
        # Р—Р°РіСЂСѓР¶Р°РµРј СЃРѕСЃС‚РѕСЏРЅРёРµ
        state = load_state(pid)
        state["total_steps"] = len(steps)
        
        if not resume:
            state["current_step"] = 0
            state["errors"] = []
            state["state"] = "new"
        
        save_state(pid, state)
        
        # Р’С‹РїРѕР»РЅСЏРµРј С€Р°РіРё
        start_step = state.get("current_step", 0)
        
        for idx in range(start_step, len(steps)):
            step = steps[idx]
            state["state"] = "running"
            state["current_step"] = idx + 1
            save_state(pid, state)
            
            try:
                msg = run_step(pid, step, state)
                print(f"[{pid}] Step {idx+1}/{len(steps)}: {step.get('type', 'unknown')} - OK")
            except Exception as e:
                state["state"] = "error"
                state.setdefault("errors", []).append(f"step {idx+1}: {e}")
                save_state(pid, state)
                return {
                    "ok": False,
                    "failed_step": idx + 1,
                    "error": str(e),
                    "last": state.get("last_message", "")
                }
        
        # РџСЂРѕРµРєС‚ Р·Р°РІРµСЂС€РµРЅ
        state["state"] = "done"
        save_state(pid, state)
        
        return {
            "ok": True,
            "message": "project finished",
            "steps": len(steps),
            "last": state.get("last_message", "")
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }
