#!/usr/bin/env python
import inspect
import sys

try:
    from src.core.game import Game
    
    # Get all methods of the Game class
    methods = inspect.getmembers(Game, predicate=inspect.isfunction)
    method_names = [name for name, _ in methods]
    
    print("Game class methods found:")
    for name in sorted(method_names):
        print(f"  - {name}")
    
    if 'run' in method_names:
        print("\n✓ run method EXISTS in Game class")
    else:
        print("\n✗ run method NOT FOUND in Game class")
        print("\nSearching for 'run' in source:")
        source = inspect.getsource(Game)
        if 'def run' in source:
            print("  'def run' found in source code")
        else:
            print("  'def run' NOT found in source code")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
