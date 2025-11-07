# Compatibility shim for legacy path: Memory/GPT+Deepseek_Agent_memory.py
# Re-exports everything from the new agent module.
try:
    from api.agent import *
except Exception as e:
    raise
