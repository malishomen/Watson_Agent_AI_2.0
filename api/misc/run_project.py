#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, sys, yaml
from pathlib import Path

AGENT = r"D:\AI-Agent\Memory\GPT+Deepseek_Agent_memory.py"

def call_agent(session: str, command: str) -> int:
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["CHCP"] = "65001"
    
    cmd = ["python", AGENT, "--session", session, "--once", command]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode

def main():
    if len(sys.argv) < 2:
        print("Usage: run_project.py D:\AI-Agent\ProjectSpec.yml")
        return 2

    spec_path = Path(sys.argv[1]).resolve()
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))

    session = data.get("defaults", {}).get("session", "Danil-PC")
    steps = data.get("steps", [])
    rc_total = 0

    for i, step in enumerate(steps, 1):
        action = step.get("action")
        print(f"\n=== Step {i}: {action} ===")

        if action == "cd":
            path = step["path"]
            rc_total |= call_agent(session, f"/cd {path}")

        elif action == "pwd":
            rc_total |= call_agent(session, "/pwd")

        elif action == "write":
            path, text = step["path"], step.get("text", "")
            rc_total |= call_agent(session, f"/write {path} ::: {text}")

        elif action == "read":
            path = step["path"]
            rc_total |= call_agent(session, f"/read {path}")

        elif action == "run":
            exe = step["exe"]
            args = step.get("args", "")
            qexe = f'"{exe}"' if (" " in exe and not exe.startswith('"')) else exe
            rc_total |= call_agent(session, f"/run {qexe} {args}".strip())

        elif action == "kill":
            target = step["target"]
            rc_total |= call_agent(session, f"/kill {target}")

        else:
            print(f"РќРµРёР·РІРµСЃС‚РЅРѕРµ РґРµР№СЃС‚РІРёРµ: {action}")
            rc_total |= 1

    print("\n=== DONE ===")
    sys.exit(rc_total)

if __name__ == "__main__":
    main()
