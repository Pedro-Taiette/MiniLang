"""Os reconhecedores que as classes da tabela léxica usam

dev_note: 
    O caso geral é `claims_symbol`/`consume_symbol` - a classe é uma linguagem finita de símbolos isolados, então as chaves de `type_by_lexeme` são o próprio conjunto
    de símbolos que ela reclama. As demais funções existem porque a classe precisa de lookahead ou de um laço de continuidade
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .alphabet import is_digit, is_ident_start, is_whitespace

if TYPE_CHECKING:
    from ..analysis.lexer import Lexer
    from .lexical_class import LexicalClass


def claims_symbol(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    return lexer.peek() in lexical_class.type_by_lexeme


def consume_symbol(lexer: Lexer, lexical_class: LexicalClass) -> None:
    lexer.advance()
    lexer.add_token(lexical_class.type_for(lexer.lexeme()))


def claims_rel_op(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    symbol = lexer.peek()
    if symbol in ("<", ">"):
        return True

    # "=" sozinho é ASSIGN e "!" sozinho é inválido - ambos só pertencem a REL_OP quando o próximo símbolo fecha o operador :) 
    return symbol in ("=", "!") and lexer.peek_next() == "="


def consume_rel_op(lexer: Lexer, lexical_class: LexicalClass) -> None:
    lexer.advance()
    lexer.match("=")    # fecha "==", "!=", "<=" e ">="; "<" e ">" seguem sozinhos
    lexer.add_token(lexical_class.type_for(lexer.lexeme()))


def claims_ident_base(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    return is_ident_start(lexer.peek())


def consume_ident_base(lexer: Lexer, lexical_class: LexicalClass) -> None:
    lexer.advance()
    lexer.identifier()


def claims_int_literal(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    return is_digit(lexer.peek())


def consume_int_literal(lexer: Lexer, lexical_class: LexicalClass) -> None:
    lexer.advance()
    lexer.number()


def claims_line_comment(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    return lexer.peek() == "/" and lexer.peek_next() == "/"


def consume_line_comment(lexer: Lexer, lexical_class: LexicalClass) -> None:
    lexer.advance()
    lexer.advance()
    lexer.line_comment()


def claims_whitespace(lexer: Lexer, lexical_class: LexicalClass) -> bool:
    return is_whitespace(lexer.peek())


def consume_whitespace(lexer: Lexer, lexical_class: LexicalClass) -> None:
    while is_whitespace(lexer.peek()):
        lexer.advance()
