# fix_respond_v2.py
import os, re

ROOT = os.getcwd()
# Ищем ТОЛЬКО сигнатуры с одним self и БЕЗ аргументов, учитываем аннотацию возврата
pat = re.compile(
    r'^(?P<indent>\s*)def\s+respond\s*\(\s*self\s*\)\s*(?P<retann>->\s*[^:]+)?\s*:',
    re.MULTILINE
)

def repl(m):
    indent = m.group('indent') or ''
    retann = m.group('retann') or ''
    return f"{indent}def respond(self, *args, **kwargs){retann}:"

changed_files = 0
changed_repls = 0
touched = []

for dp, _, files in os.walk(ROOT):
    for name in files:
        if not name.endswith(".py"):
            continue
        path = os.path.join(dp, name)
        try:
            s = open(path, "r", encoding="utf-8", errors="replace").read()
        except Exception as e:
            print(f"[skip] {path}: {e}")
            continue

        new_s, n = pat.subn(repl, s)
        if n:
            open(path + ".bak", "w", encoding="utf-8", newline="\n").write(s)
            open(path, "w", encoding="utf-8", newline="\n").write(new_s)
            changed_files += 1
            changed_repls += n
            touched.append(path)

print(f"Updated files: {changed_files}, replacements: {changed_repls}")
for p in touched:
    print(" -", os.path.relpath(p, ROOT))
