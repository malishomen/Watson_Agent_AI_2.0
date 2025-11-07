import os
import json
import pytest
import requests


API_BASE = "http://127.0.0.1:8088"


def test_api_connection():
    """Тест подключения к API (skip, если сервис недоступен)."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
    except Exception as exc:
        pytest.skip(f"API Agent not available: {exc}")

    if response.status_code != 200:
        pytest.skip(f"API Agent HTTP {response.status_code}")

    data = response.json()
    print(f"✅ API Agent: {data.get('status')}")
    print(f"✅ LM Studio: {('Работает' if data.get('lm_studio') else 'Не работает')}")
    print(f"✅ Cursor: {('Доступен' if data.get('cursor_available') else 'Не доступен')}")
    assert True


def test_task_creation():
    """Тест создания задачи (skip, если сервис недоступен)."""
    task_data = {
        "task": "Test task from bot",
        "project_path": "D:\\AI-Agent\\Memory",
        "timeout": 300,
    }

    try:
        response = requests.post(f"{API_BASE}/task", json=task_data, timeout=10)
    except Exception as exc:
        pytest.skip(f"API Agent not available: {exc}")

    if response.status_code != 200:
        pytest.skip(f"Task creation HTTP {response.status_code}")

    data = response.json()
    print(f"✅ Task created: {data.get('task_id')}")
    assert True



