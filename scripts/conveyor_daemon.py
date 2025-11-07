#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conveyor Daemon - Автоматическое планирование и выполнение задач из backlog
Читает PROJECT_BACKLOG.md, создаёт задачи в inbox/, останавливается при ошибках
"""
import os
import sys
import time
import json
import glob
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Добавляем путь к utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

INBOX = Path(__file__).parent.parent / "inbox"
LOG_FILE = Path(__file__).parent.parent / "data" / "conveyor.log"
PROJECTS_ROOT = Path("D:/projects/Projects_by_Watson_Local_Agent")
CHECK_INTERVAL = 30  # секунды


def log(message: str, level: str = "INFO"):
    """Логирование в файл и stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    
    # Stdout
    print(log_line)
    
    # File
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"Log write error: {e}")


def parse_backlog(backlog_path: Path) -> List[Dict[str, any]]:
    """
    Парсит PROJECT_BACKLOG.md и извлекает задачи
    
    Формат:
    ## Backlog
    - [ ] Task 1 description (priority: high)
    - [ ] Task 2 description
    - [x] Completed task
    """
    if not backlog_path.exists():
        return []
    
    tasks = []
    try:
        with open(backlog_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ищем незавершённые задачи
        pattern = r'- \[ \] (.+?)(?:\(priority:\s*(\w+)\))?$'
        for match in re.finditer(pattern, content, re.MULTILINE):
            task_text = match.group(1).strip()
            priority = match.group(2) or "normal"
            
            tasks.append({
                "text": task_text,
                "priority": priority.lower(),
                "completed": False
            })
        
        # Сортируем по приоритету
        priority_order = {"high": 0, "normal": 1, "low": 2}
        tasks.sort(key=lambda t: priority_order.get(t["priority"], 1))
        
        log(f"Parsed {len(tasks)} tasks from {backlog_path.name}")
        return tasks
        
    except Exception as e:
        log(f"Error parsing backlog: {e}", "ERROR")
        return []


def check_last_task_status() -> Optional[str]:
    """
    Проверяет статус последней задачи по логам
    Возвращает: "success", "failed", None
    """
    try:
        if not LOG_FILE.exists():
            return None
        
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Ищем последний результат
        for line in reversed(lines[-50:]):  # последние 50 строк
            if "TASK COMPLETED" in line:
                return "success"
            if "TASK FAILED" in line or "RED BUILD" in line:
                return "failed"
        
        return None
    except Exception as e:
        log(f"Error checking task status: {e}", "ERROR")
        return None


def create_task_file(task: Dict[str, any]):
    """Создаёт .task.json в inbox/"""
    try:
        INBOX.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        task_file = INBOX / f"{timestamp}-backlog.task.json"
        
        task_data = {
            "text": task["text"],
            "dry_run": False,
            "priority": task["priority"],
            "source": "conveyor_daemon"
        }
        
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
        
        log(f"Created task: {task_file.name} | {task['text'][:60]}...")
        return True
    except Exception as e:
        log(f"Error creating task file: {e}", "ERROR")
        return False


def scan_projects() -> List[Path]:
    """Сканирует проекты и ищет PROJECT_BACKLOG.md"""
    projects = []
    
    try:
        if not PROJECTS_ROOT.exists():
            log(f"Projects root not found: {PROJECTS_ROOT}", "WARN")
            return projects
        
        for project_dir in PROJECTS_ROOT.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                backlog = project_dir / "PROJECT_BACKLOG.md"
                if backlog.exists():
                    projects.append(project_dir)
        
        log(f"Found {len(projects)} projects with backlog")
        return projects
    except Exception as e:
        log(f"Error scanning projects: {e}", "ERROR")
        return []


def main():
    """Основной цикл daemon"""
    log("="*60)
    log("Conveyor Daemon started")
    log(f"Inbox: {INBOX.absolute()}")
    log(f"Projects: {PROJECTS_ROOT.absolute()}")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log("="*60)
    
    consecutive_failures = 0
    MAX_FAILURES = 3
    
    while True:
        try:
            # Проверяем статус последней задачи
            last_status = check_last_task_status()
            
            if last_status == "failed":
                consecutive_failures += 1
                log(f"RED BUILD detected ({consecutive_failures}/{MAX_FAILURES})", "WARN")
                
                if consecutive_failures >= MAX_FAILURES:
                    log(f"Stopping after {MAX_FAILURES} consecutive failures", "ERROR")
                    log("Fix the errors and restart daemon", "ERROR")
                    break
            else:
                consecutive_failures = 0
            
            # Сканируем проекты
            projects = scan_projects()
            
            if not projects:
                log("No projects with backlog found, sleeping...", "INFO")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # Обрабатываем по одной задаче за итерацию
            task_created = False
            for project_dir in projects:
                backlog_path = project_dir / "PROJECT_BACKLOG.md"
                tasks = parse_backlog(backlog_path)
                
                if tasks:
                    # Берём первую задачу
                    next_task = tasks[0]
                    log(f"Next task from {project_dir.name}: {next_task['text'][:60]}...")
                    
                    # Создаём задачу
                    if create_task_file(next_task):
                        task_created = True
                        
                        # Помечаем задачу как взятую в работу
                        try:
                            with open(backlog_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            
                            # Заменяем первую [ ] на [~] (в работе)
                            content = content.replace("- [ ] " + next_task["text"], 
                                                    "- [~] " + next_task["text"], 1)
                            
                            with open(backlog_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            
                            log(f"Marked task as in-progress in {backlog_path.name}")
                        except Exception as e:
                            log(f"Error updating backlog: {e}", "WARN")
                        
                        break  # Одна задача за цикл
            
            if not task_created:
                log("No pending tasks found, sleeping...", "INFO")
            
            # Пауза
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("Daemon stopped by user (Ctrl+C)", "INFO")
            break
        except Exception as e:
            log(f"Daemon error: {e}", "ERROR")
            time.sleep(CHECK_INTERVAL)
    
    log("="*60)
    log("Conveyor Daemon stopped")
    log("="*60)


if __name__ == "__main__":
    main()



