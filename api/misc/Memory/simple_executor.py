# Simple Executor - РџСЂРѕСЃС‚РѕР№ РёСЃРїРѕР»РЅРёС‚РµР»СЊ Р·Р°РґР°С‡
# РЎРѕР·РґР°РЅРёРµ С„Р°Р№Р»РѕРІ Рё РІС‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡ Р±РµР· UI Р°РІС‚РѕРјР°С‚РёР·Р°С†РёРё

import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime

def get_pending_tasks():
    """РџРѕР»СѓС‡РµРЅРёРµ СЃРїРёСЃРєР° РѕР¶РёРґР°СЋС‰РёС… Р·Р°РґР°С‡"""
    try:
        tasks_dir = Path("tasks")
        if not tasks_dir.exists():
            return []
        
        pending_tasks = []
        for task_file in tasks_dir.glob("*.json"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                    if task_data.get("status") == "pending":
                        pending_tasks.append({
                            "file": task_file,
                            "data": task_data
                        })
            except Exception as e:
                print(f"вќЊ РћС€РёР±РєР° С‡С‚РµРЅРёСЏ Р·Р°РґР°С‡Рё {task_file}: {e}")
        
        return pending_tasks
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ Р·Р°РґР°С‡: {e}")
        return []

def create_task_file(task_description, task_id):
    """РЎРѕР·РґР°РЅРёРµ С„Р°Р№Р»Р° Р·Р°РґР°С‡Рё"""
    try:
        # РЎРѕР·РґР°РµРј РґРёСЂРµРєС‚РѕСЂРёСЋ РґР»СЏ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ
        results_dir = Path("task_results")
        results_dir.mkdir(exist_ok=True)
        
        # РЎРѕР·РґР°РµРј С„Р°Р№Р» СЃ РѕРїРёСЃР°РЅРёРµРј Р·Р°РґР°С‡Рё
        task_file = results_dir / f"{task_id}.md"
        
        content = f"""# Р—Р°РґР°С‡Р°: {task_description}

**ID Р·Р°РґР°С‡Рё:** {task_id}
**Р”Р°С‚Р° СЃРѕР·РґР°РЅРёСЏ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**РЎС‚Р°С‚СѓСЃ:** Р’ РїСЂРѕС†РµСЃСЃРµ РІС‹РїРѕР»РЅРµРЅРёСЏ

## РћРїРёСЃР°РЅРёРµ Р·Р°РґР°С‡Рё

{task_description}

## Р РµР·СѓР»СЊС‚Р°С‚ РІС‹РїРѕР»РЅРµРЅРёСЏ

Р—Р°РґР°С‡Р° Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РѕР±СЂР°Р±РѕС‚Р°РЅР° СЃРёСЃС‚РµРјРѕР№ AI Agent + Cursor Automation.

## РЎР»РµРґСѓСЋС‰РёРµ С€Р°РіРё

1. РћС‚РєСЂРѕР№С‚Рµ Cursor Editor
2. РРјРїРѕСЂС‚РёСЂСѓР№С‚Рµ РїСЂРѕРµРєС‚
3. РџСЂРѕРґРѕР»Р¶РёС‚Рµ СЂР°Р·СЂР°Р±РѕС‚РєСѓ

---
*РЎРѕР·РґР°РЅРѕ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё СЃРёСЃС‚РµРјРѕР№ AI Agent*
"""
        
        with open(task_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"вњ… РЎРѕР·РґР°РЅ С„Р°Р№Р» Р·Р°РґР°С‡Рё: {task_file}")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ С„Р°Р№Р»Р° Р·Р°РґР°С‡Рё: {e}")
        return False

def create_project_structure(task_description):
    """РЎРѕР·РґР°РЅРёРµ СЃС‚СЂСѓРєС‚СѓСЂС‹ РїСЂРѕРµРєС‚Р°"""
    try:
        # РЎРѕР·РґР°РµРј Р±Р°Р·РѕРІСѓСЋ СЃС‚СЂСѓРєС‚СѓСЂСѓ РїСЂРѕРµРєС‚Р°
        project_dir = Path("generated_project")
        project_dir.mkdir(exist_ok=True)
        
        # РЎРѕР·РґР°РµРј README.md
        readme_file = project_dir / "README.md"
        readme_content = f"""# {task_description}

РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРё СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅС‹Р№ РїСЂРѕРµРєС‚ СЃРёСЃС‚РµРјРѕР№ AI Agent.

## РЎС‚СЂСѓРєС‚СѓСЂР° РїСЂРѕРµРєС‚Р°

```
generated_project/
в”њв”Ђв”Ђ README.md
в”њв”Ђв”Ђ main.py
в”њв”Ђв”Ђ requirements.txt
в””в”Ђв”Ђ .gitignore
```

## РЈСЃС‚Р°РЅРѕРІРєР°

```bash
pip install -r requirements.txt
```

## Р—Р°РїСѓСЃРє

```bash
python main.py
```

---
*РЎРѕР·РґР°РЅРѕ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # РЎРѕР·РґР°РµРј main.py
        main_file = project_dir / "main.py"
        main_content = f'''# {task_description}

import os
from datetime import datetime

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    print("рџљЂ {task_description}")
    print(f"рџ“… Р”Р°С‚Р°: {{datetime.now()}}")
    print("вњ… РџСЂРѕРµРєС‚ РіРѕС‚РѕРІ Рє СЂР°Р±РѕС‚Рµ!")

if __name__ == "__main__":
    main()
'''
        
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(main_content)
        
        # РЎРѕР·РґР°РµРј requirements.txt
        requirements_file = project_dir / "requirements.txt"
        requirements_content = """# Р—Р°РІРёСЃРёРјРѕСЃС‚Рё РїСЂРѕРµРєС‚Р°
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
"""
        
        with open(requirements_file, "w", encoding="utf-8") as f:
            f.write(requirements_content)
        
        # РЎРѕР·РґР°РµРј .gitignore
        gitignore_file = project_dir / ".gitignore"
        gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        with open(gitignore_file, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        
        print(f"вњ… РЎРѕР·РґР°РЅР° СЃС‚СЂСѓРєС‚СѓСЂР° РїСЂРѕРµРєС‚Р°: {project_dir}")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° СЃРѕР·РґР°РЅРёСЏ СЃС‚СЂСѓРєС‚СѓСЂС‹ РїСЂРѕРµРєС‚Р°: {e}")
        return False

def mark_task_completed(task_file, task_data):
    """РћС‚РјРµС‚РєР° Р·Р°РґР°С‡Рё РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅРѕР№"""
    try:
        task_data["status"] = "completed"
        task_data["completed_at"] = time.time()
        task_data["result"] = "Р¤Р°Р№Р»С‹ СЃРѕР·РґР°РЅС‹ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё"
        
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        print(f"вњ… Р—Р°РґР°С‡Р° {task_file.name} РѕС‚РјРµС‡РµРЅР° РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅР°СЏ")
        return True
        
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° РѕС‚РјРµС‚РєРё Р·Р°РґР°С‡Рё: {e}")
        return False

def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ"""
    print("рџ¤– Simple Executor - РџСЂРѕСЃС‚РѕР№ РёСЃРїРѕР»РЅРёС‚РµР»СЊ Р·Р°РґР°С‡")
    print("=" * 60)
    
    # РџСЂРѕРІРµСЂСЏРµРј API Р°РіРµРЅС‚
    try:
        response = requests.get("http://127.0.0.1:8088/health", timeout=5)
        if response.status_code != 200:
            print("вќЊ API Р°РіРµРЅС‚ РЅРµ СЂР°Р±РѕС‚Р°РµС‚")
            return
        print("вњ… API Р°РіРµРЅС‚ СЂР°Р±РѕС‚Р°РµС‚")
    except:
        print("вќЊ API Р°РіРµРЅС‚ РЅРµРґРѕСЃС‚СѓРїРµРЅ")
        return
    
    # РџРѕР»СѓС‡Р°РµРј РѕР¶РёРґР°СЋС‰РёРµ Р·Р°РґР°С‡Рё
    pending_tasks = get_pending_tasks()
    
    if not pending_tasks:
        print("рџ“‹ РќРµС‚ РѕР¶РёРґР°СЋС‰РёС… Р·Р°РґР°С‡")
        return
    
    print(f"рџ“‹ РќР°Р№РґРµРЅРѕ Р·Р°РґР°С‡: {len(pending_tasks)}")
    
    # Р’С‹РїРѕР»РЅСЏРµРј Р·Р°РґР°С‡Рё
    completed_tasks = 0
    for task_info in pending_tasks:
        task_file = task_info["file"]
        task_data = task_info["data"]
        task_description = task_data.get("task", "РќРµРёР·РІРµСЃС‚РЅР°СЏ Р·Р°РґР°С‡Р°")
        task_id = task_file.stem
        
        print(f"\n--- Р’С‹РїРѕР»РЅРµРЅРёРµ Р·Р°РґР°С‡Рё ---")
        print(f"рџ“ќ РћРїРёСЃР°РЅРёРµ: {task_description}")
        print(f"рџ†” ID: {task_id}")
        
        # РЎРѕР·РґР°РµРј С„Р°Р№Р» Р·Р°РґР°С‡Рё
        if create_task_file(task_description, task_id):
            # РЎРѕР·РґР°РµРј СЃС‚СЂСѓРєС‚СѓСЂСѓ РїСЂРѕРµРєС‚Р°
            if create_project_structure(task_description):
                # РћС‚РјРµС‡Р°РµРј РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅСѓСЋ
                if mark_task_completed(task_file, task_data):
                    completed_tasks += 1
                    print(f"вњ… Р—Р°РґР°С‡Р° {task_id} РІС‹РїРѕР»РЅРµРЅР°")
                else:
                    print(f"вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РјРµС‚РёС‚СЊ Р·Р°РґР°С‡Сѓ РєР°Рє РІС‹РїРѕР»РЅРµРЅРЅСѓСЋ")
            else:
                print(f"вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ СЃС‚СЂСѓРєС‚СѓСЂСѓ РїСЂРѕРµРєС‚Р°")
        else:
            print(f"вќЊ РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР·РґР°С‚СЊ С„Р°Р№Р» Р·Р°РґР°С‡Рё")
        
        # РџР°СѓР·Р° РјРµР¶РґСѓ Р·Р°РґР°С‡Р°РјРё
        time.sleep(1)
    
    print(f"\n" + "=" * 60)
    print(f"рџ“Љ Р РµР·СѓР»СЊС‚Р°С‚:")
    print(f"вњ… Р’С‹РїРѕР»РЅРµРЅРѕ Р·Р°РґР°С‡: {completed_tasks}")
    print(f"рџ“ќ Р’СЃРµРіРѕ Р·Р°РґР°С‡: {len(pending_tasks)}")
    
    if completed_tasks > 0:
        print(f"\nрџЋЇ Р—Р°РґР°С‡Рё РІС‹РїРѕР»РЅРµРЅС‹!")
        print(f"рџ“Ѓ РџСЂРѕРІРµСЂСЊС‚Рµ РїР°РїРєРё:")
        print(f"   - task_results/ - С„Р°Р№Р»С‹ Р·Р°РґР°С‡")
        print(f"   - generated_project/ - СЃС‚СЂСѓРєС‚СѓСЂР° РїСЂРѕРµРєС‚Р°")
        print(f"рџ’Ў РћС‚РєСЂРѕР№С‚Рµ Cursor Рё РёРјРїРѕСЂС‚РёСЂСѓР№С‚Рµ generated_project/")

if __name__ == "__main__":
    main()





