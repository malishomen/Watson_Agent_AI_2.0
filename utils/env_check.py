from __future__ import annotations

import os
import sys
from typing import Iterable, List


REQUIRED_ENV_VARS = [
    "OPENAI_BASE_URL",
    "OPENAI_API_KEY",
    "TELEGRAM_TOKEN",
    "DATABASE_URL",
]


class MissingEnvError(RuntimeError):
    pass


def check_required_env(required_vars: Iterable[str] = REQUIRED_ENV_VARS) -> List[str]:
    missing: List[str] = [var for var in required_vars if not os.environ.get(var)]
    return missing


def ensure_required_env(required_vars: Iterable[str] = REQUIRED_ENV_VARS) -> None:
    missing = check_required_env(required_vars)
    if missing:
        raise MissingEnvError(
            "; ".join(
                [
                    "Не хватает секретов: " + ", ".join(missing),
                    "Введите их вручную в PowerShell и перезапустите агент.",
                ]
            )
        )


if __name__ == "__main__":
    missing = check_required_env()
    if missing:
        print(f"❌ Не хватает секретов: {', '.join(missing)}")
        print("Введите их вручную в PowerShell и перезапустите агент.")
        sys.exit(1)
    print("✅ Все ключи на месте, продолжаем…")
    sys.exit(0)


