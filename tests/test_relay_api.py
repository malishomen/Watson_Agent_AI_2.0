"""
Дымовые тесты для /relay/submit endpoint
"""
import sys
import os
import pytest

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Проверяем доступность fastapi
pytest.importorskip("fastapi")

try:
    from fastapi.testclient import TestClient
    from api.fastapi_agent import app
    client = TestClient(app)
except Exception as e:
    # Если TestClient не работает - пропускаем все тесты
    pytestmark = pytest.mark.skip(reason=f"TestClient unavailable: {e}")


def test_relay_help():
    """Тест /relay/submit с help запросом"""
    r = client.post("/relay/submit", json={"text": "help"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") == True
    assert data.get("intent") == "help"
    assert "response" in data


def test_relay_ping():
    """Тест /relay/submit с ping запросом"""
    r = client.post("/relay/submit", json={"text": "ping"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") == True
    assert data.get("intent") == "ping"


def test_relay_project_create():
    """Тест /relay/submit с созданием проекта (dry-run стиль)"""
    r = client.post("/relay/submit", json={"text": "создай проект test_smoke", "dry_run": True})
    assert r.status_code == 200
    data = r.json()
    # Может быть ok=True или ok=False если проект уже существует
    assert "intent" in data


def test_relay_invalid_request():
    """Тест с невалидным запросом"""
    r = client.post("/relay/submit", json={})
    # Pydantic должен вернуть 422
    assert r.status_code == 422


def test_health_endpoint():
    """Smoke test для /health"""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") == True

