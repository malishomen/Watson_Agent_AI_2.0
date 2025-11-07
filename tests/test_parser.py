#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from parsers.nlp_command_router import parse_free_text

def test_parser():
    print("=== Тест парсера команд ===")
    
    test_cases = [
        "запусти notepad",
        "покажи процессы", 
        "прочитай README.md",
        "где я",
        "терминал dir",
        "run calc.exe",
        "show processes"
    ]
    
    for test in test_cases:
        result = parse_free_text(test)
        print(f"'{test}' -> '{result}'")

if __name__ == "__main__":
    test_parser()
