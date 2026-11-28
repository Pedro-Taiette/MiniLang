"""Tipos de token da MiniLang e o registro que o lexer produz"""

from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    KW_INT = "KW_INT"
    KW_BOOL = "KW_BOOL"
    KW_PRINT = "KW_PRINT"
    KW_IF = "KW_IF"
    KW_ELSE = "KW_ELSE"
    KW_WHILE = "KW_WHILE"
    KW_FOR = "KW_FOR"           # extensao: fora do escopo obrigatorio do trabalho final

    IDENT = "IDENT"
    INT_LITERAL = "INT_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"

    AND = "AND"
    OR = "OR"

    ASSIGN = "ASSIGN"

    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"

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

    # aparece uma unica vez, com lexema vazio
    EOF = "EOF"


# Consultada so depois de ler o identificador inteiro: ANDx e trueValue continuam IDENT
KEYWORDS = {
    "int": TokenType.KW_INT,
    "bool": TokenType.KW_BOOL,
    "print": TokenType.KW_PRINT,
    "if": TokenType.KW_IF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE,
    "for": TokenType.KW_FOR,
    "true": TokenType.BOOL_LITERAL,
    "false": TokenType.BOOL_LITERAL,
    "AND": TokenType.AND,
    "OR": TokenType.OR,
}

# "!" nao esta aqui de proposito: sozinho ele e invalido, so existe em "!="
SYMBOLS = {
    "=": TokenType.ASSIGN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "==": TokenType.EQUAL_EQUAL,
    "!=": TokenType.BANG_EQUAL,
    "<": TokenType.LESS,
    "<=": TokenType.LESS_EQUAL,
    ">": TokenType.GREATER,
    ">=": TokenType.GREATER_EQUAL,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ";": TokenType.SEMICOLON,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __str__(self) -> str:
        return f'{self.type.value}("{self.lexeme}") {self.line}:{self.column}'
