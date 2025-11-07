"""
Profile Loader - загрузка конфигурации из YAML профилей
Использование: WATSON_PROFILE=staging python ...
"""
import os
import re
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None


def expand_env_vars(value: Any) -> Any:
    """Рекурсивно заменяет ${VAR} на значения из env"""
    if isinstance(value, str):
        # Заменяем ${VAR} и $VAR
        pattern = r'\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)'
        
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(pattern, replacer, value)
    
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        return [expand_env_vars(item) for item in value]
    
    return value


def load_profile(profile_name: str = None) -> Dict[str, Any]:
    """
    Загружает профиль из config/profiles/{profile_name}.yml
    
    Args:
        profile_name: Имя профиля (local/staging/prod) или None для auto-detect
    
    Returns:
        Dict с конфигурацией
    """
    if yaml is None:
        # Fallback без YAML
        return _load_fallback(profile_name)
    
    # Определяем профиль
    if not profile_name:
        profile_name = os.getenv("WATSON_PROFILE", "local")
    
    # Путь к файлу
    config_dir = Path(__file__).parent.parent / "config" / "profiles"
    profile_file = config_dir / f"{profile_name}.yml"
    
    if not profile_file.exists():
        print(f"[PROFILE] Warning: {profile_file} not found, using fallback")
        return _load_fallback(profile_name)
    
    # Загружаем YAML
    try:
        with open(profile_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Подставляем env vars
        config = expand_env_vars(config)
        
        print(f"[PROFILE] Loaded: {profile_name}")
        return config
    
    except Exception as e:
        print(f"[PROFILE] Error loading {profile_file}: {e}")
        return _load_fallback(profile_name)


def _load_fallback(profile_name: str) -> Dict[str, Any]:
    """Fallback конфигурация без YAML"""
    return {
        "environment": profile_name or "local",
        "api": {
            "base_url": os.getenv("WATSON_API_BASE", "http://127.0.0.1:8090"),
            "timeout": 300
        },
        "llm": {
            "base_url": os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "lm-studio"),
            "planner_model": os.getenv("WATSON_PLANNER_MODEL", "deepseek-r1"),
            "coder_model": os.getenv("WATSON_CODER_MODEL", "qwen2.5-coder-7b-instruct")
        },
        "paths": {
            "repo_path": os.getcwd(),
            "projects_root": "D:\\projects\\Projects_by_Watson_Local_Agent"
        },
        "testing": {
            "test_cmd": "py -3.11 -m pytest -q"
        }
    }


def get_config(key: str, default: Any = None) -> Any:
    """
    Получает значение из текущего профиля
    
    Args:
        key: Путь к ключу через точку (например "api.base_url")
        default: Значение по умолчанию
    
    Returns:
        Значение конфигурации
    """
    config = load_profile()
    
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


# Кэш профиля
_cached_profile = None


def get_current_profile() -> Dict[str, Any]:
    """Возвращает текущий профиль (с кэшированием)"""
    global _cached_profile
    
    if _cached_profile is None:
        _cached_profile = load_profile()
    
    return _cached_profile



