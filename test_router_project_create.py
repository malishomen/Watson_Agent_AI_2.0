#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from utils.nlp_router import _fallback_normalize

# Тест создания проекта
test_cases = [
    "создай проект калькулятор",
    "создай проект генератор случайных чисел от 1 до 1000",
    "create project todo_app",
]

for test in test_cases:
    result = _fallback_normalize(test)
    print(f"\nInput: {test}")
    print(f"Intent: {result['intent']}")
    print(f"Project name: {result.get('project_name', 'N/A')}")
    print(f"Full: {json.dumps(result, ensure_ascii=False, indent=2)}")

