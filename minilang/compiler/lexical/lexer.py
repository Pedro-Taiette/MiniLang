"""Varredura manual da MiniLang

dev_note:
    O lexer mantém um cursor sobre o código-fonte e não divide a entrada previamente. `scan_token` não decide nada sozinho: pergunta à tabela léxica qual
    classe é dona da posição atual e deixa a classe consumir o lexema

    Toda a atualização de linha e coluna fica em `advance`, inclusive a de `match`
"""

from ..common.cursor import Cursor
from ..common.diagnostics import Diagnostic, Phase
from .alphabet import is_digit, is_ident_continue, is_line_break, is_source_symbol
from .table import RESERVED_WORDS, SCAN_TABLE
from .tokens import Token, TokenType


class Lexer(Cursor):
    END = ""        # peek devolve a cadeia vazia no fim da entrada

    def __init__(self, source: str):
        # CRLF vira um único NL para que a quebra conte uma linha só
        super().__init__(source.replace("\r\n", "\n"))

        self.start = 0          # Indice do primeiro símbolo do lexema atual
        self.line = 1           # Posicao associada a current (current position do cursor)
        self.column = 1         # Idem
        self.start_line = 1     # posicao do primeiro simbolo do lexema atual
        self.start_column = 1   # Idem

        # -- Saidas -------
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    # --- Grupo 1 --- Olhar sem consumir (at_end, peek e check vêm de Cursor)
    def peek_next(self) -> str:
        return self.peek(1)

    # --- Grupo 2 --- Consumir (match vem de Cursor e passa por este advance)
    def advance(self) -> str:
        symbol = super().advance()

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

    # --- Grupo 4 --- Orquestração de classes léxicas
    def scan_tokens(self) -> tuple[list[Token], list[Diagnostic]]:
        # Uma volta = um lexema, que pode ser um token ou um erro - evita o loop infinito de relatar o mesmo erro várias vezes
        while not self.at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column

            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens, self.diagnostics

    def scan_token(self) -> None:
        # Divergecia do enunciado. Ao inves de uma cadeida de if/elif, a responsabilidade de reconhecer o lexema é delegada a cada classe léxica. Isso permite que a tabela seja facilmente estendida com novas classes.
        for lexical_class in SCAN_TABLE:
            if lexical_class.claims_at(self):
                lexical_class.consume_at(self)
                return

        # Consumir antes de relatar garante progresso
        self.report_invalid_character(self.advance())

    # --- Grupo 5 --- Os Continuadores
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
