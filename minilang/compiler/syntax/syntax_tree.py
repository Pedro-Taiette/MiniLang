"""Nós da árvore sintática abstrata (AST) da MiniLang

dev_note:
    Os nós só guardam dados: o parser constrói e a análise semântica anota (os campos que começam em None)
    label() é como o nó aparece na saída e segue o enunciado. children() são os filhos, na ordem do código-fonte
    Parênteses não viram nó: o agrupamento já está na forma da árvore
"""

from dataclasses import dataclass

from ..lexical.tokens import Token
from .grammar import COMPARISON_OPERATORS


# --- Expressões ---
@dataclass
class Integer:
    literal: Token
    type: object = None

    def label(self) -> str:
        return f"Inteiro({self.literal.lexeme})"       # o lexema como veio: 007 não vira 7

    def children(self) -> list:
        return []


@dataclass
class Boolean:
    literal: Token
    type: object = None

    def label(self) -> str:
        return f"Booleano({self.literal.lexeme})"

    def children(self) -> list:
        return []


@dataclass
class Variable:
    name: Token
    symbol: object = None
    type: object = None

    def label(self) -> str:
        return f"Variavel({self.name.lexeme})"

    def children(self) -> list:
        return []


@dataclass
class Binary:
    operator: Token
    left: object
    right: object
    type: object = None

    def label(self) -> str:
        if self.operator.type in COMPARISON_OPERATORS:
            return f"Relacional({self.operator.lexeme})"
        return f"Binaria({self.operator.lexeme})"

    def children(self) -> list:
        return [self.left, self.right]


# --- Comandos ---
@dataclass
class Declaration:
    keyword: Token          # 'int' ou 'bool'
    name: Token
    symbol: object = None

    def label(self) -> str:
        return f"Declaracao({self.name.lexeme})"

    def children(self) -> list:
        return []


@dataclass
class Assignment:
    name: Token
    value: object
    symbol: object = None

    def label(self) -> str:
        return f"Atribuicao({self.name.lexeme})"

    def children(self) -> list:
        return [self.value]


@dataclass
class Output:
    value: object

    def label(self) -> str:
        return "Saida"

    def children(self) -> list:
        return [self.value]


@dataclass
class Block:
    brace: Token            # o '{', que dá a posição do escopo
    items: list
    scope: object = None

    def label(self) -> str:
        return "Bloco"

    def children(self) -> list:
        return self.items


@dataclass
class If:
    keyword: Token
    condition: object
    then_branch: Block
    else_branch: Block | None

    def label(self) -> str:
        return "If"

    def children(self) -> list:
        if self.else_branch is None:
            return [self.condition, self.then_branch]
        return [self.condition, self.then_branch, self.else_branch]


@dataclass
class While:
    keyword: Token
    condition: object
    body: Block

    def label(self) -> str:
        return "While"

    def children(self) -> list:
        return [self.condition, self.body]


@dataclass
class For:
    keyword: Token
    initializer: object     # as três partes do cabeçalho podem faltar (None)
    condition: object
    increment: object
    body: Block
    scope: object = None

    def label(self) -> str:
        return "For"

    def children(self) -> list:
        children = []
        for part in [self.initializer, self.condition, self.increment]:
            if part is not None:
                children.append(part)
        children.append(self.body)
        return children


@dataclass
class Program:
    items: list

    def label(self) -> str:
        return "Programa"

    def children(self) -> list:
        return self.items
