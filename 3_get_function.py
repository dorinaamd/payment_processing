"""Step 7 (zoom in): print the full body of ONE function.

Usage:  python 3_get_function.py payment_processing/order_service.py OrderService.process
"""
import ast
import sys

path, target = sys.argv[1], sys.argv[2]
src = open(path).read()
cls, fn = target.split(".")
for c in ast.parse(src).body:
    if isinstance(c, ast.ClassDef) and c.name == cls:
        for m in c.body:
            if isinstance(m, ast.FunctionDef) and m.name == fn:
                print("\n".join(src.splitlines()[m.lineno - 1 : m.end_lineno]))
