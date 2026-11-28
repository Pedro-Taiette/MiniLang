"""Analise lexica de um arquivo-fonte

    dev_note: python main.py examples/programa.min
"""

import sys

from minilang.compiler.lexical.lexer import Lexer
from minilang.compiler.syntax.parser import Parser
from minilang.compiler.syntax.tree_printer import format_tree

sys.stdout.reconfigure(encoding="utf-8")

with open(sys.argv[1], encoding="utf-8", newline="") as file:
    source = file.read()

tokens, lexical_diagnostics = Lexer(source).scan_tokens()

print("Tokens:")
for token in tokens:
    print(f"  {token}")

print("\nDiagnostico léxico:")
if lexical_diagnostics:
    for diagnostic in lexical_diagnostics:
        print(f"  {diagnostic}")
else:
    print("  Não houveram erros")

# a gente prossegue se n tem bugs no diagnóstico léxico

if lexical_diagnostics:
    print("\nAnalise sintatica nao executada: ha erros lexicos")
    sys.exit(1)

program, syntax_diagnostics = Parser(tokens).parse()

print("\nDiagnóstico sintatico:")
if syntax_diagnostics:
    for diagnostic in syntax_diagnostics:
        print(f"  {diagnostic}")
    sys.exit(1) # pq n tem como prosseguir depois disso
else:
    print("  Não houveram erros")

print("\nAST (a arvore binária):")
print(format_tree(program))