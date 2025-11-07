#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from utils.nlp_router import _fallback_normalize

test_cases = [
    "сделай логирование в safe_call",
    "привет",
    "/ping",
    "Add logging to function X",
]

for test in test_cases:
    result = _fallback_normalize(test)
    print(f"\nInput: {test}")
    print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")

