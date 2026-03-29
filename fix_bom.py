#!/usr/bin/env python
# Read with BOM handling and rewrite without BOM
with open('src/core/game.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Write back without BOM
with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Removed BOM from game.py")

# Verify it compiles now
import py_compile
try:
    py_compile.compile('src/core/game.py', doraise=True)
    print("✓ game.py compiles successfully")
except py_compile.PyCompileError as e:
    print(f"✗ Compilation error: {e}")
