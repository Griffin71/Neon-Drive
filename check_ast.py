#!/usr/bin/env python
import ast
import sys

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()
    tree = ast.parse(content)

game_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Game':
        game_class = node
        break

with open('ast_check.txt', 'w') as out:
    if game_class:
        methods = [n.name for n in game_class.body if isinstance(n, ast.FunctionDef)]
        out.write(f'Found {len(methods)} methods in Game\n')
        out.write(f'Methods: {", ".join(methods)}\n')
        if 'run' in methods:
            out.write('✓ run method FOUND\n')
        else:
            out.write('✗ run method NOT FOUND\n')
    else:
        out.write('Game class not found\n')
