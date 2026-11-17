"""Step 2: turn a folder of .py files into a short structural skeleton.

Keeps: file names, which sibling modules each file uses, classes,
       method signatures, first line of each docstring.
Drops: every method body.

Usage:  python 2_make_skeleton.py payment_processing > skeleton.txt
"""
import ast
import sys
from pathlib import Path

for path in sorted(Path(sys.argv[1]).rglob("*.py")):
    tree = ast.parse(path.read_text())
    print(f"# {path.name}")
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level > 0:      # "from .x import Y"
            print(f"  uses: {node.module}.{node.names[0].name}")
        elif isinstance(node, ast.ClassDef):
            bases = ", ".join(ast.unparse(b) for b in node.bases)
            print(f"  class {node.name}({bases})" if bases else f"  class {node.name}")
            for m in node.body:
                if isinstance(m, ast.FunctionDef):
                    doc = (ast.get_docstring(m) or "").split("\n")[0]
                    print(f"    def {m.name}({ast.unparse(m.args)}) -> "
                          f"{ast.unparse(m.returns) if m.returns else 'None'}"
                          f"{'  # ' + doc if doc else ''}")
    print()
