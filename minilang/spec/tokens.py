"""Tipos de token da MiniLang e os registros que o lexer produz"""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    # KEYWORD_CORE e KEYWORD_EXT: reclassificam um lexema já reconhecido como IDENT_BASE
    KW_INT = "KW_INT"
    KW_PRINT = "KW_PRINT"
    KW_IF = "KW_IF"
    KW_ELSE = "KW_ELSE"
    KW_WHILE = "KW_WHILE"

    IDENT = "IDENT"
    INT_LITERAL = "INT_LITERAL"

    ASSIGN = "ASSIGN"

    # ARITH_OP
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"

    # REL_OP
    EQUAL_EQUAL = "EQUAL_EQUAL"
    BANG_EQUAL = "BANG_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    SEMICOLON = "SEMICOLON"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"

    # Situação de fim de entrada, não classe léxica - aparece uma única vez, com lexema vazio
    EOF = "EOF"


# WHITESPACE e LINE_COMMENT não têm TokenType - são reconhecidos e descartados, LOgo nunca chegam à lista de tokens

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"{self.type.value}({self.lexeme!r}) em {self.line}:{self.column}"


@dataclass(frozen=True)
class Diagnostic:
    symbol: str
    line: int
    column: int
    message: str

    def __str__(self) -> str:
        return f"{self.line}:{self.column}: {self.message}"
