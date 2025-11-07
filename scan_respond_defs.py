import os, ast
root = os.getcwd()
bad = []
for dp,_,fs in os.walk(root):
    for f in fs:
        if not f.endswith(".py"): continue
        p = os.path.join(dp,f)
        try:
            src = open(p,"r",encoding="utf-8",errors="replace").read()
            tree = ast.parse(src,p)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef, ast.AsyncFunctionDef)) and node.name=="respond":
                parent = getattr(node, "parent", None)
        # привяжем родителей (простая проходка)
        for n in ast.walk(tree):
            for ch in ast.iter_child_nodes(n):
                ch.parent = n
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in [x for x in cls.body if isinstance(x,(ast.FunctionDef, ast.AsyncFunctionDef)) and x.name=="respond"]:
                args = fn.args
                # считаем *после* self
                a = [a.arg for a in args.args]
                after_self = a[1:] if a and a[0]=="self" else a
                has_vararg = args.vararg is not None
                if not after_self and not has_vararg:
                    kind = "async" if isinstance(fn, ast.AsyncFunctionDef) else "def"
                    bad.append((p, fn.lineno, kind))
for p,ln,kind in bad:
    print(f"{p}:{ln}: {kind} respond(self)  <-- узкая сигнатура")
