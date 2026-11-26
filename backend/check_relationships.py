import ast, pathlib

classes, rels = {}, []
for f in sorted(pathlib.Path('app/models').glob('*.py')):
    tree = ast.parse(f.read_text(encoding='utf-8'))
    for c in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        attrs = set()
        for n in c.body:
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
                name, value, ann = n.target.id, n.value, n.annotation
            elif isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                name, value, ann = n.targets[0].id, n.value, None
            else:
                continue
            attrs.add(name)
            if isinstance(value, ast.Call) and getattr(value.func, 'id', getattr(value.func, 'attr', '')) == 'relationship':
                target = None
                if value.args and isinstance(value.args[0], ast.Constant):
                    target = value.args[0].value
                elif ann is not None:
                    strs = [x.value for x in ast.walk(ann) if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                    target = strs[0] if strs else None
                back = None
                for kw in value.keywords:
                    if kw.arg in ('back_populates', 'backref') and isinstance(kw.value, ast.Constant):
                        back = (kw.arg, kw.value.value)
                rels.append((c.name, name, target, back, f.name, n.lineno))
        classes[c.name] = (f.name, attrs)

print('---- relationships whose other side is missing ----')
bad = 0
for owner, attr, target, back, fn, ln in rels:
    if not back or back[0] != 'back_populates':
        continue
    if target not in classes:
        print(f'{fn}:{ln}: {owner}.{attr} -> unknown class {target!r}'); bad += 1
    elif back[1] not in classes[target][1]:
        print(f'{fn}:{ln}: {owner}.{attr} expects {target}.{back[1]}, but {target} (in {classes[target][0]}) has no "{back[1]}"'); bad += 1
print('none' if not bad else f'{bad} problem(s)')

print('\n---- WeeklyReport ----')
if 'WeeklyReport' in classes:
    print('file:', classes['WeeklyReport'][0])
    print('attributes:', sorted(classes['WeeklyReport'][1]))
