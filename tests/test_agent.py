#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pytest
import os
sys.path.append('D:/AI-Agent')

# РРјРїРѕСЂС‚РёСЂСѓРµРј Р°РіРµРЅС‚Р°
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent", "api/agent.py")
    agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent_module)
    respond = agent_module.respond
    print("вњ… РђРіРµРЅС‚ РёРјРїРѕСЂС‚РёСЂРѕРІР°РЅ СѓСЃРїРµС€РЅРѕ")
except ImportError as e:
    print(f"вќЊ РћС€РёР±РєР° РёРјРїРѕСЂС‚Р° Р°РіРµРЅС‚Р°: {e}")
    sys.exit(1)

@pytest.mark.integration
def test_agent():
    print("=== РўРµСЃС‚ Р°РіРµРЅС‚Р° ===")
    
    try:
        # РўРµСЃС‚РёСЂСѓРµРј РїСЂРѕСЃС‚СѓСЋ РєРѕРјР°РЅРґСѓ
        result = respond(1, "/pwd")
        print(f"вњ… /pwd -> {result}")
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° /pwd: {e}")
    
    try:
        # РўРµСЃС‚РёСЂСѓРµРј РєРѕРјР°РЅРґСѓ Р·Р°РїСѓСЃРєР°
        result = respond(1, "/run notepad")
        print(f"вњ… /run notepad -> {result}")
    except Exception as e:
        print(f"вќЊ РћС€РёР±РєР° /run notepad: {e}")

if __name__ == "__main__":
    test_agent()

