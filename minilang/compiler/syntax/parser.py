"""Análise sintática da MiniLang: parser descendente recursivo

dev_note:
    Um método por não-terminal da gramática (spec/grammar.py), com a produção na docstring
    O token atual escolhe a produção. Nas expressões, quanto mais embaixo o método, mais cedo o operador agrupa
    advance nunca passa do EOF - o lexer garante que ele é o último token
"""

from ..common.cursor import Cursor
from ..common.diagnostics import Diagnostic, Phase
from ..lexical.tokens import Token, TokenType
from .grammar import (ADDITIVE_OPERATORS, AND_OPERATORS, COMPARISON_OPERATORS, MULTIPLICATIVE_OPERATORS,
                      OR_OPERATORS)
from .syntax_tree import (Assignment, Binary, Block, Boolean, Declaration, For, If, Integer, Output, Program,
                          Variable, While)


class ParseError(Exception):
    """Só desenrola a pilha até parse() - nunca sai do módulo"""

    def __init__(self, diagnostic: Diagnostic):
        self.diagnostic = diagnostic


class Parser(Cursor):

    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)

    # --- Grupo 1 --- Olhar sem consumir (peek vem de Cursor)
    def check(self, token_type: TokenType) -> bool:
        return self.peek().type == token_type

    def at_end(self) -> bool:
        return self.check(TokenType.EOF)

    # --- Grupo 2 --- Consumir (advance e match vêm de Cursor e usam o check e o at_end acima)
    def expect(self, token_type: TokenType, expected: str) -> Token:
        if self.check(token_type):
            return self.advance()

        raise self.error(expected)

    # --- Grupo 3 --- Diagnóstico
    def error(self, expected: str) -> ParseError:
        token = self.peek()
        if self.at_end():
            found = "fim da entrada"
        else:
            found = repr(token.lexeme)

        message = f"esperado {expected}, encontrado {found}"
        return ParseError(Diagnostic(Phase.SYNTAX, token.line, token.column, message, token.lexeme))

    # --- Grupo 4 --- Programa e comandos
    def parse(self):
        try:
            return self.program(), []
        except ParseError as error:
            return None, [error.diagnostic]
        except RecursionError:
            token = self.peek()
            message = "expressao aninhada demais"
            return None, [Diagnostic(Phase.SYNTAX, token.line, token.column, message, token.lexeme)]

    def program(self) -> Program:
        """Program -> ItemList"""
        items = self.item_list()
        self.expect(TokenType.EOF, "fim da entrada")
        return Program(items)

    def item_list(self) -> list:
        """ItemList -> Item ItemList | empty"""
        items = []
        # a lista acaba no '}' de um bloco ou no fim da entrada
        while not self.check(TokenType.RBRACE) and not self.at_end():
            items.append(self.item())
        return items

    def item(self):
        """Item -> Declaration | Assignment | Output | Block | If | While | For"""
        if self.check(TokenType.KW_INT) or self.check(TokenType.KW_BOOL):
            return self.declaration()
        if self.check(TokenType.IDENT):
            return self.assignment()
        if self.check(TokenType.KW_PRINT):
            return self.output()
        if self.check(TokenType.LBRACE):
            return self.block()
        if self.check(TokenType.KW_IF):
            return self.if_statement()
        if self.check(TokenType.KW_WHILE):
            return self.while_statement()
        if self.check(TokenType.KW_FOR):
            return self.for_statement()

        raise self.error("comando ('int', 'bool', 'print', 'if', 'while', 'for', '{' ou identificador)")

    def declaration(self) -> Declaration:
        """Declaration -> Type IDENT SEMICOLON"""
        keyword = self.advance()        # 'int' ou 'bool': quem chamou já conferiu
        name = self.expect(TokenType.IDENT, "identificador")
        self.expect(TokenType.SEMICOLON, "';'")
        return Declaration(keyword, name)

    def assignment(self) -> Assignment:
        """Assignment -> IDENT ASSIGN Expression SEMICOLON"""
        assignment = self.increment()
        self.expect(TokenType.SEMICOLON, "';'")
        return assignment

    def increment(self) -> Assignment:
        """Increment -> IDENT ASSIGN Expression    (a atribuição sem o ';', que no for é fechada pelo ')')"""
        name = self.expect(TokenType.IDENT, "identificador")
        self.expect(TokenType.ASSIGN, "'='")
        value = self.expression()
        return Assignment(name, value)

    def output(self) -> Output:
        """Output -> KW_PRINT LPAREN Expression RPAREN SEMICOLON"""
        self.expect(TokenType.KW_PRINT, "'print'")
        value = self.parenthesized()
        self.expect(TokenType.SEMICOLON, "';'")
        return Output(value)

    def block(self) -> Block:
        """Block -> LBRACE ItemList RBRACE"""
        brace = self.expect(TokenType.LBRACE, "'{'")
        items = self.item_list()
        self.expect(TokenType.RBRACE, "'}'")
        return Block(brace, items)

    def if_statement(self) -> If:
        """If -> KW_IF LPAREN Expression RPAREN Block Else"""
        keyword = self.expect(TokenType.KW_IF, "'if'")
        condition = self.parenthesized()
        then_branch = self.block()

        # Else -> KW_ELSE Block | empty
        else_branch = None
        if self.match(TokenType.KW_ELSE):
            else_branch = self.block()

        return If(keyword, condition, then_branch, else_branch)

    def while_statement(self) -> While:
        """While -> KW_WHILE LPAREN Expression RPAREN Block"""
        keyword = self.expect(TokenType.KW_WHILE, "'while'")
        condition = self.parenthesized()
        body = self.block()
        return While(keyword, condition, body)

    def for_statement(self) -> For:
        """For -> KW_FOR LPAREN Initializer Condition SEMICOLON Increment RPAREN Block"""
        keyword = self.expect(TokenType.KW_FOR, "'for'")
        self.expect(TokenType.LPAREN, "'('")

        # Initializer -> Declaration | Assignment | SEMICOLON
        initializer = None
        if self.check(TokenType.KW_INT) or self.check(TokenType.KW_BOOL):
            initializer = self.declaration()
        elif not self.match(TokenType.SEMICOLON):
            initializer = self.assignment()

        # Condition -> Expression | empty
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.expect(TokenType.SEMICOLON, "';'")

        # Increment -> IDENT ASSIGN Expression | empty
        increment = None
        if not self.check(TokenType.RPAREN):
            increment = self.increment()
        self.expect(TokenType.RPAREN, "')'")

        body = self.block()
        return For(keyword, initializer, condition, increment, body)

    # --- Grupo 5 --- Expressões, da menor precedência para a maior
    def expression(self):
        """Expression -> Conjunction Expression'"""
        left = self.conjunction()
        while self.peek().type in OR_OPERATORS:
            operator = self.advance()
            right = self.conjunction()
            left = Binary(operator, left, right)
        return left

    def conjunction(self):
        """Conjunction -> Comparison Conjunction'"""
        left = self.comparison()
        while self.peek().type in AND_OPERATORS:
            operator = self.advance()
            right = self.comparison()
            left = Binary(operator, left, right)
        return left

    def comparison(self):
        """Comparison -> Addition Comparison'"""
        left = self.addition()
        # aqui é if, não while: só uma comparação, a < b < c é erro
        if self.peek().type in COMPARISON_OPERATORS:
            operator = self.advance()
            right = self.addition()
            left = Binary(operator, left, right)
        return left

    def addition(self):
        """Addition -> Term Addition'"""
        left = self.term()
        # o que já foi lido vira o filho esquerdo: 10 - 3 - 2 fica (10 - 3) - 2
        while self.peek().type in ADDITIVE_OPERATORS:
            operator = self.advance()
            right = self.term()
            left = Binary(operator, left, right)
        return left

    def term(self):
        """Term -> Factor Term'"""
        left = self.factor()
        while self.peek().type in MULTIPLICATIVE_OPERATORS:
            operator = self.advance()
            right = self.factor()
            left = Binary(operator, left, right)
        return left

    def factor(self):
        """Factor -> LPAREN Expression RPAREN | IDENT | INT_LITERAL | BOOL_LITERAL"""
        if self.check(TokenType.LPAREN):
            return self.parenthesized()

        if self.check(TokenType.IDENT):
            return Variable(self.advance())

        if self.check(TokenType.INT_LITERAL):
            return Integer(self.advance())

        if self.check(TokenType.BOOL_LITERAL):
            return Boolean(self.advance())

        raise self.error("numero, identificador ou '('")

    # LPAREN Expression RPAREN - usado pelo print, pelo if, pelo while e pelo fator
    def parenthesized(self):
        self.expect(TokenType.LPAREN, "'('")
        expression = self.expression()
        self.expect(TokenType.RPAREN, "')'")
        return expression
