"""Varredura manual da MiniLang

dev_note:
    O lexer mantém um cursor sobre o código-fonte e não divide a entrada previamente. `scan_token` não decide nada sozinho: pergunta à tabela léxica qual
    classe é dona da posição atual e deixa a classe consumir o lexema

    Toda a atualização de linha e coluna fica em `advance`, inclusive a de `match`
"""

from ..spec.alphabet import is_digit, is_ident_continue, is_line_break, is_source_symbol
from ..spec.table import RESERVED_WORDS, SCAN_TABLE
from ..spec.tokens import Diagnostic, Token, TokenType


class Lexer:

    def __init__(self, source: str):
        # CRLF vira um único NL para que a quebra conte uma linha só
        self.source = source.replace("\r\n", "\n")

        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    def scan_tokens(self) -> tuple[list[Token], list[Diagnostic]]:
        while not self.at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column

            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.diagnostics

    def scan_token(self) -> None:
        for lexical_class in SCAN_TABLE:
            if lexical_class.claims_at(self):
                lexical_class.consume_at(self)
                return

        # Consumir antes de relatar garante progresso
        self.report_invalid_character(self.advance())

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        symbol = self.source[self.current]
        self.current += 1

        if is_line_break(symbol):
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return symbol

    def peek(self) -> str:
        if self.at_end():
            return ""
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return ""
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.peek() != expected:
            return False

        self.advance()
        return True

    def lexeme(self) -> str:
        return self.source[self.start:self.current]

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
            Diagnostic(symbol, self.start_line, self.start_column, message)
        )

    def identifier(self) -> None:
        while is_ident_continue(self.peek()):
            self.advance()

        # A consulta só acontece com o identificador inteiro na mão - é o que faz intx, ifx e while1 continuarem IDENT
        self.add_token(RESERVED_WORDS.get(self.lexeme(), TokenType.IDENT))

    def number(self) -> None:
        while is_digit(self.peek()):
            self.advance()

        self.add_token(TokenType.INT_LITERAL)

    def line_comment(self) -> None:
        # A quebra não é consumida: o próximo scan_token a reconhece como WHITESPACE
        while not self.at_end() and not is_line_break(self.peek()):
            self.advance()
