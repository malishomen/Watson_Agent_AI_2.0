# Test System - Тесты для системы AI Agent + Cursor Automation
# Проверка всех компонентов системы

import pytest
import requests
import subprocess
import os
import sys
from pathlib import Path

class TestSystem:
    """Тесты системы"""
    
    def test_python_available(self):
        """Проверка доступности Python"""
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "Python" in result.stdout
    
    def test_cursor_available(self):
        """Проверка доступности Cursor"""
        try:
            result = subprocess.run(["cursor", "--version"], capture_output=True, text=True)
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("Cursor not found in PATH")
    
    def test_lm_studio_available(self):
        """Проверка доступности LM Studio"""
        try:
            response = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("LM Studio not running")
    
    def test_api_agent_available(self):
        """Проверка доступности API агента"""
        try:
            response = requests.get("http://127.0.0.1:8088/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("API Agent not running")
    
    def test_project_structure(self):
        """Проверка структуры проекта"""
        required_files = [
            "README.md",
            "requirements.txt",
            "api/agent.py",
            "automation/cursor_automation.py",
            "automation/cursor_automation.ps1",
            "scripts/start_system.ps1",
            "scripts/setup_autorun.ps1"
        ]
        
        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file not found: {file_path}"
    
    def test_python_packages(self):
        """Проверка Python пакетов"""
        required_packages = [
            "fastapi",
            "uvicorn",
            "pyautogui",
            "PIL",  # pillow импортируется как PIL
            "keyboard",
            "requests"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package not installed: {package}")

@pytest.mark.integration
def test_health_check():
    """Тест проверки здоровья системы"""
    try:
        response = requests.get("http://127.0.0.1:8088/health", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "lm_studio" in data
        assert "cursor_available" in data
        
    except requests.exceptions.RequestException:
        pytest.skip("API Agent not running")

@pytest.mark.integration
def test_task_creation():
    """Тест создания задачи"""
    try:
        task_data = {
            "task": "Create test application",
            "project_path": "D:\\AI-Agent\\fresh_start",
            "timeout": 300
        }
        
        response = requests.post("http://127.0.0.1:8088/task", json=task_data, timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "task_id" in data
        
    except requests.exceptions.RequestException:
        pytest.skip("API Agent not running")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
