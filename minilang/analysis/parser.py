
"""Análise sintática da MiniLang: descendente recursiva, um método por não-terminal

dev_note:
    O parser mantém um cursor sobre a lista de tokens. Toda leitura passa por peek/advance/match/expect, e advance
    nunca passa do EOF - o lexer garante que ele é o último token

    Correspondência com o enunciado: programa -> program, lista_itens -> item_list, item -> item,
    declaracao -> declaration, atribuicao -> assignment, saida -> output, expressao -> expression,
    termo -> term, fator -> factor
"""

from ..spec.grammar import ADDITIVE_OPERATORS, MULTIPLICATIVE_OPERATORS
from ..spec.syntax_tree import (
    Assignment,
    Binary,
    Declaration,
    Expression,
    Integer,
    Item,
    Output,
    Program,
    Variable,
    If,
    While,
    For,
    Block,
    Relational
)
from ..spec.tokens import Diagnostic, Token, TokenType


class ParseError(Exception):
    """Só desenrola a pilha até parse() - nunca sai do módulo"""

    def __init__(self, diagnostic: Diagnostic):
        super().__init__(str(diagnostic))
        self.diagnostic = diagnostic


class Parser:

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    # --- Grupo 1 --- Olhar sem consumir
    def at_end(self) -> bool:
        return self.peek().type is TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    # --- Grupo 2 --- Consumir
    def advance(self) -> Token:
        token = self.peek()
        if not self.at_end():
            self.current += 1
        return token

    def match(self, *types: TokenType) -> bool:
        if self.peek().type not in types:
            return False

        self.advance()
        return True

    def expect(self, token_type: TokenType, expected: str) -> Token:
        if self.peek().type is token_type:
            return self.advance()

        raise self.error(expected)

    # --- Grupo 3 --- Diagnóstico
    def error(self, expected: str) -> ParseError:
        token = self.peek()
        found = (
            "fim da entrada"
            if token.type is TokenType.EOF
            else repr(token.lexeme)
        )

        return ParseError(Diagnostic(
            token.lexeme,
            token.line,
            token.column,
            f"esperado {expected}, encontrado {found}"
        ))

    # --- Grupo 4 --- Entrada pública
    def parse(self) -> tuple[Program | None, list[Diagnostic]]:
        try:
            return self.program(), []
        except ParseError as error:
            return None, [error.diagnostic]
        except RecursionError:
            token = self.peek()
            return None, [Diagnostic(token.lexeme, token.line, token.column, "expressao aninhada demais")]

    # --- Grupo 5 --- Comandos (Fase 4 - Pessoa 5)
    def program(self) -> Program:
        items = self.item_list()
        self.expect(TokenType.EOF, "fim da entrada")
        return Program(tuple(items))

    def item_list(self) -> list[Item]:
        items = []

        while not self.at_end():
            items.append(self.item())

        return items

    def item(self) -> Item:
        token_type = self.peek().type

        if token_type is TokenType.KW_INT:
            return self.declaration()

        if token_type is TokenType.IDENT:
            return self.assignment()

        if token_type is TokenType.KW_PRINT:
            return self.output()
        
        if token_type is TokenType.KW_IF:
            return self.if_statement()
        
        if token_type is TokenType.KW_WHILE:
            return self.while_statement()
        
        if token_type is TokenType.KW_FOR:
            return self.for_statement()

        raise self.error("comando ('int', 'print', 'if', 'while', 'for' ou identificador)")

    def assignment(self) -> Assignment:
        name = self.expect(TokenType.IDENT, "identificador")
        self.expect(TokenType.ASSIGN, "'='")
        value = self.expression()
        self.expect(TokenType.SEMICOLON, "';'")
        return Assignment(name, value)

    # --- Declaração
    def declaration(self) -> Declaration:
        self.expect(TokenType.KW_INT, "'int'")
        name = self.expect(TokenType.IDENT, "identificador")
        self.expect(TokenType.SEMICOLON, "';'")
        return Declaration(name)

    # --- Saída
    def output(self) -> Output:
        self.expect(TokenType.KW_PRINT, "'print'")
        self.expect(TokenType.LPAREN, "'('")
        value = self.expression()
        self.expect(TokenType.RPAREN, "')'")
        self.expect(TokenType.SEMICOLON, "';'")
        return Output(value)

    # --- Expressões
    def expression(self) -> Expression:
        left = self.term()

        while self.peek().type in ADDITIVE_OPERATORS:
            operator = self.advance()
            right = self.term()
            left = Binary(operator, left, right)

        return left

    def term(self) -> Expression:
        left = self.factor()

        while self.peek().type in MULTIPLICATIVE_OPERATORS:
            operator = self.advance()
            right = self.factor()
            left = Binary(operator, left, right)

        return left

    def factor(self) -> Expression:
        token = self.peek()

        if token.type is TokenType.INT_LITERAL:
            return Integer(self.advance())

        if token.type is TokenType.IDENT:
            return Variable(self.advance())

        if self.match(TokenType.LPAREN):
            inner = self.expression()
            self.expect(TokenType.RPAREN, "')'")
            return inner

        raise self.error("numero, identificador ou '('")

    def block(self) -> Block:
        self.expect(TokenType.LBRACE, "'{'")
        items = []
        while not self.at_end() and self.peek().type is not TokenType.RBRACE:
            items.append(self.item())
        self.expect(TokenType.RBRACE, "'}'")
        return Block(tuple(items))

    def condition(self) -> Expression:
        left = self.expression()
        rel_ops = {TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS, 
                    TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL}
        
        if self.peek().type in rel_ops:
            operator = self.advance()
            right = self.expression()
            return Relational(operator, left, right)
        return left

    def if_statement(self) -> If:
        self.expect(TokenType.KW_IF, "'if'")
        self.expect(TokenType.LPAREN, "'('")
        cond = self.condition()
        self.expect(TokenType.RPAREN, "')'")
        then_branch = self.block()
        else_branch = None
        
        if self.match(TokenType.KW_ELSE):
            else_branch = self.block()
            
        return If(cond, then_branch, else_branch)

    def while_statement(self) -> While:
        self.expect(TokenType.KW_WHILE, "'while'")
        self.expect(TokenType.LPAREN, "'('")
        cond = self.condition()
        self.expect(TokenType.RPAREN, "')'")
        body = self.block()
        return While(cond, body)

    def for_statement(self) -> For:
        self.expect(TokenType.KW_FOR, "'for'")
        self.expect(TokenType.LPAREN, "'('")
        
        initializer = None
        if self.peek().type is not TokenType.SEMICOLON:
            if self.peek().type is TokenType.KW_INT:
                initializer = self.declaration()
            else:
                initializer = self.assignment()
        else:
            self.advance() # Consome o ';' vazio
            
        cond = None
        if self.peek().type is not TokenType.SEMICOLON:
            cond = self.condition()
        self.expect(TokenType.SEMICOLON, "';'")
        
        increment = None
        if self.peek().type is not TokenType.RPAREN:
            increment = self.assignment()
            
        self.expect(TokenType.RPAREN, "')'")
        body = self.block()
        
        return For(initializer, cond, increment, body)
