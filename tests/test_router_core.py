"""
Тесты для utils/router_core.py
"""
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.router_core import slugify, plan_and_route


def test_slugify_basic():
    """Базовый тест slugify"""
    assert slugify("ToDo App!") == "todo_app"
    assert slugify("   ") == "project"
    assert slugify("My-Cool_Project") == "my_cool_project"
    assert slugify("Test123") == "test123"


def test_slugify_cyrillic():
    """Тест транслитерации (если добавлена в slugify)"""
    result = slugify("Проект Тест")
    # Пока просто проверяем, что не падает и возвращает что-то разумное
    assert isinstance(result, str)
    assert len(result) > 0


def test_plan_and_route_help():
    """Тест роутинга для help команды"""
    result = plan_and_route("help")
    assert result.get("intent") == "help"
    assert "response" in result


def test_plan_and_route_ping():
    """Тест роутинга для ping команды"""
    result = plan_and_route("ping")
    assert result.get("intent") == "ping"
    assert "response" in result


def test_plan_and_route_project_create():
    """Тест определения создания проекта"""
    result = plan_and_route("создай проект test_app")
    assert result.get("intent") == "project_create"
    assert result.get("project_name") == "test_app"


def test_plan_and_route_code_fallback():
    """Тест fallback на код без LLM"""
    result = plan_and_route("add logging to main.py", llm_client=None)
    assert result.get("intent") == "code"
    assert result.get("normalized_text") == "add logging to main.py"



