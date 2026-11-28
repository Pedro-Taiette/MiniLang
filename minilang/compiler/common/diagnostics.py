"""Diagnóstico de compilação: o mesmo registro para as três fases de análise"""

from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    LEXICAL = "lexica"
    SYNTAX = "sintatica"
    SEMANTIC = "semantica"


@dataclass(frozen=True)
class Diagnostic:
    phase: Phase
    line: int
    column: int
    message: str
    lexeme: str = ""        # o símbolo ou token que causou o erro

    def __str__(self) -> str:
        return f"{self.line}:{self.column}: {self.message}"
