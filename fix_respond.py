# fix_respond.py
import os, re

ROOT = os.getcwd()
pat = re.compile(r'^(?P<indent>\s*)def\s+respond\s*\(\s*self\s*\)\s*:', re.MULTILINE)

changed_files = 0
changed_repls = 0
touched = []

for dp, _, files in os.walk(ROOT):
    for name in files:
        if not name.endswith(".py"):
            continue
        path = os.path.join(dp, name)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                s = f.read()
        except Exception as e:
            print(f"[skip] {path}: {e}")
            continue

        new_s, n = pat.subn(r"\g<indent>def respond(self, *args, **kwargs):", s)
        if n:
            with open(path + ".bak", "w", encoding="utf-8", newline="\n") as b:
                b.write(s)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_s)
            changed_files += 1
            changed_repls += n
            touched.append(path)

print(f"Updated files: {changed_files}, replacements: {changed_repls}")
for p in touched:
    print(" -", os.path.relpath(p, ROOT))
