"""Analise lexica de um arquivo-fonte

    dev_note: python main.py examples/programa.min
"""

import sys

from minilang.analysis.lexer import Lexer

sys.stdout.reconfigure(encoding="utf-8")

with open(sys.argv[1], encoding="utf-8", newline="") as file:
    source = file.read()

tokens, diagnostics = Lexer(source).scan_tokens()

print("Tokens:")
for token in tokens:
    print(f"  {token}")

print("\nDiagnosticos:")
for diagnostic in diagnostics:
    print(f"  {diagnostic}")
