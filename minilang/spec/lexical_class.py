"""O tipo de uma classe léxica

dev_note:
    Cada classe carrega a própria definição - a teórica, que vai para a documentação, e a executável, que é o par de funções abaixo

        claims(lexer, lexical_class)  -> diz se a classe é dona da posição atual, consultando no máximo dois símbolos (`peek` e `peek_next`) e SEM CONSUMIR NADA
        consume(lexer, lexical_class) -> consome o lexema com `advance`/`match` e emite

    Nenhuma classe indexa o código-fonte diretamente - tudo passa pelas operações do lexer, que é onde linha e coluna são atualizadas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable

from .tokens import TokenType

if TYPE_CHECKING:
    from ..analysis.lexer import Lexer


class Action(Enum):
    EMITS = "emitido ao parser"
    IGNORES = "reconhecido e ignorado"
    RECLASSIFIES = "reclassifica o lexema de outra classe"


@dataclass(frozen=True)
class LexicalClass:
    name: str                                   # 1, com finalidade
    purpose: str
    description: str                            # 2
    examples: tuple[str, ...]                   # 3
    mathematical_definition: str                # 4
    formal_expression: str                      # 6
    action: Action
    finite_language: bool                       # slide 96 (da aula 03) cobra mínimos diferentes

    auxiliary_sets: tuple[str, ...] = ()        # 5, só quando a estrutura exigir

    # 8: a implementação é o par type_by_lexeme/type mais o reconhecedor
    type: TokenType | None = None
    type_by_lexeme: dict[str, TokenType] = field(default_factory=dict)

    claims: Callable[[Lexer, LexicalClass], bool] | None = None
    consume: Callable[[Lexer, LexicalClass], None] | None = None

    def claims_at(self, lexer: Lexer) -> bool:
        return self.claims(lexer, self)

    def consume_at(self, lexer: Lexer) -> None:
        self.consume(lexer, self)

    def type_for(self, lexeme: str) -> TokenType:
        token_type = self.type_by_lexeme.get(lexeme, self.type)
        if token_type is None:
            raise KeyError(f"{self.name} nao classifica {lexeme!r}")
        return token_type
