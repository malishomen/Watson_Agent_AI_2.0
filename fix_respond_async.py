import os, re

ROOT = os.getcwd()
pat = re.compile(
    r'(?m)^(?P<indent>\s*)(?P<async>async\s+)?def\s+respond\s*\(\s*self\s*\)\s*(?P<retann>->\s*[^:]+)?\s*:',
    re.MULTILINE
)

def repl(m):
    indent = m.group('indent') or ''
    async_kw = m.group('async') or ''
    retann = m.group('retann') or ''
    return f"{indent}{async_kw}def respond(self, *args, **kwargs){retann}:"

changed_files = 0
changed_repls = 0
touched = []

for dp, _, files in os.walk(ROOT):
    for name in files:
        if not name.endswith(".py"): continue
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
