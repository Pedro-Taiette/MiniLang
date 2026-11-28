"""Varredura manual da MiniLang: lê o código-fonte símbolo a símbolo e devolve tokens e diagnósticos"""

from ..common.cursor import Cursor
from ..common.diagnostics import Diagnostic, Phase
from .alphabet import (CARRIAGE_RETURN, NEWLINE, is_digit, is_ident_continue, is_ident_start, is_line_break,
                       is_source_symbol, is_whitespace)
from .tokens import KEYWORDS, SYMBOLS, Token, TokenType


class Lexer(Cursor):
    END = ""        # peek devolve a cadeia vazia no fim da entrada

    def __init__(self, source: str):
        super().__init__(source)

        self.start = 0          # indice do primeiro simbolo do lexema atual
        self.line = 1           # posicao do cursor
        self.column = 1
        self.start_line = 1     # posicao do primeiro simbolo do lexema atual
        self.start_column = 1

        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    # --- Grupo 1 --- Olhar sem consumir (at_end, peek e check vêm de Cursor)
    def peek_next(self) -> str:
        return self.peek(1)

    # --- Grupo 2 --- Consumir (match vem de Cursor e passa por este advance)
    def advance(self) -> str:
        symbol = super().advance()

        # no CRLF quem conta a quebra é o NL, senao seriam duas linhas
        if symbol == CARRIAGE_RETURN and self.peek() == NEWLINE:
            return symbol

        if is_line_break(symbol):
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return symbol

    # --- Grupo 3 --- Produzir saídas
    def lexeme(self) -> str:
        return self.items[self.start:self.current]

    def add_token(self, token_type: TokenType) -> None:
        self.tokens.append(
            Token(token_type, self.lexeme(), self.start_line, self.start_column)
        )

    def report_invalid_character(self, symbol: str) -> None:
        if is_source_symbol(symbol):
            message = f"simbolo {symbol!r} nao inicia nenhum lexema da MiniLang"
        else:
            message = f"simbolo {symbol!r} fora do alfabeto da MiniLang"

        self.diagnostics.append(
            Diagnostic(Phase.LEXICAL, self.start_line, self.start_column, message, symbol)
        )

    # --- Grupo 4 --- Varredura
    def scan_tokens(self) -> tuple[list[Token], list[Diagnostic]]:
        while not self.at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column

            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.diagnostics

    def scan_token(self) -> None:
        symbol = self.peek()

        if is_whitespace(symbol):
            self.advance()
        elif symbol == "/" and self.peek_next() == "/":
            self.line_comment()
        elif is_ident_start(symbol):
            self.identifier()
        elif is_digit(symbol):
            self.number()
        else:
            self.operator()

    # --- Grupo 5 --- Um método por tipo de lexema
    def identifier(self) -> None:
        while is_ident_continue(self.peek()):
            self.advance()

        self.add_token(KEYWORDS.get(self.lexeme(), TokenType.IDENT))

    def number(self) -> None:
        while is_digit(self.peek()):
            self.advance()

        self.add_token(TokenType.INT_LITERAL)

    def line_comment(self) -> None:
        # a quebra fica de fora, o proximo scan_token trata ela como espaço
        while not self.at_end() and not is_line_break(self.peek()):
            self.advance()

    def operator(self) -> None:
        symbol = self.advance()

        if symbol in ("=", "!", "<", ">"):
            self.match("=")     # fecha ==, !=, <= e >=

        if self.lexeme() in SYMBOLS:
            self.add_token(SYMBOLS[self.lexeme()])
        else:
            # consumir antes de relatar garante que a varredura anda
            self.report_invalid_character(symbol)
