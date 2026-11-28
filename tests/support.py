"""Atalhos que os testes do parser em diante usam para chegar do código-fonte até a AST"""

from minilang.compiler.lexical.lexer import Lexer
from minilang.compiler.syntax.parser import Parser


def tokenize(source: str) -> list:
    tokens, diagnostics = Lexer(source).scan_tokens()
    assert diagnostics == [], f"erro lexico em {source!r}: {diagnostics}"
    return tokens


def parse(source: str):
    return Parser(tokenize(source)).parse()


def compact(node) -> str:
    """A árvore em uma linha: o rótulo do nó e, entre colchetes, os filhos"""
    children = node.children()
    if not children:
        return node.label()

    return node.label() + "[" + ", ".join(compact(child) for child in children) + "]"
