"""Testes do parser. As árvores são comparadas em uma linha: o rótulo do nó e, entre colchetes, os filhos"""

import pytest

from minilang.analysis.parser import ParseError, Parser
from minilang.spec.tokens import TokenType

from .support import compact, parse, tokenize


def test_cursor():
    parser = Parser(tokenize("x;"))
    assert not parser.match(TokenType.PLUS)
    assert parser.match(TokenType.IDENT)

    with pytest.raises(ParseError) as raised:
        parser.expect(TokenType.IDENT, "identificador")
    assert str(raised.value.diagnostic) == "1:2: esperado identificador, encontrado ';'"

    parser.advance()
    assert parser.advance().type is TokenType.EOF       # advance nunca passa do EOF
    assert parser.at_end()


EXPRESSIONS = [
    # Trabalho 02, slide 6
    ("2 + 3 * 4", "Binaria(+)[Inteiro(2), Binaria(*)[Inteiro(3), Inteiro(4)]]"),
    ("(2 + 3) * 4", "Binaria(*)[Binaria(+)[Inteiro(2), Inteiro(3)], Inteiro(4)]"),
    ("10 - 3 - 2", "Binaria(-)[Binaria(-)[Inteiro(10), Inteiro(3)], Inteiro(2)]"),
    ("((x))", "Variavel(x)"),
    # Comparação e operadores lógicos
    ("x + 1 < 10", "Relacional(<)[Binaria(+)[Variavel(x), Inteiro(1)], Inteiro(10)]"),
    ("a or b and c", "Binaria(or)[Variavel(a), Binaria(and)[Variavel(b), Variavel(c)]]"),
    ("ativo and x < 10", "Binaria(and)[Variavel(ativo), Relacional(<)[Variavel(x), Inteiro(10)]]"),
]


@pytest.mark.parametrize("source, expected", EXPRESSIONS)
def test_expression(source, expected):
    parser = Parser(tokenize(source))
    node = parser.expression()
    assert parser.at_end()
    assert compact(node) == expected


PROGRAMS = [
    ("", "Programa"),
    ("print(y);", "Programa[Saida[Variavel(y)]]"),
    ("int x;\nx = 2 + 3 * 4;\nprint(x);",
     "Programa[Declaracao(x), Atribuicao(x)[Binaria(+)[Inteiro(2), Binaria(*)[Inteiro(3), Inteiro(4)]]], "
     "Saida[Variavel(x)]]"),
    ("bool b; b = true;", "Programa[Declaracao(b), Atribuicao(b)[Booleano(true)]]"),
    ("{ int y; { } }", "Programa[Bloco[Declaracao(y), Bloco]]"),
    ("if (1 < 2) {} else {}", "Programa[If[Relacional(<)[Inteiro(1), Inteiro(2)], Bloco, Bloco]]"),
    ("while (x > 0) { }", "Programa[While[Relacional(>)[Variavel(x), Inteiro(0)], Bloco]]"),
    ("for (;;) { }", "Programa[For[Bloco]]"),
    ("for (int i; i < 3; i = i + 1) { }",
     "Programa[For[Declaracao(i), Relacional(<)[Variavel(i), Inteiro(3)], "
     "Atribuicao(i)[Binaria(+)[Variavel(i), Inteiro(1)]], Bloco]]"),
]


@pytest.mark.parametrize("source, expected", PROGRAMS)
def test_program(source, expected):
    program, diagnostics = parse(source)
    assert diagnostics == []
    assert compact(program) == expected


SYNTAX_ERRORS = [
    ("print(2 + );", "1:11: esperado numero, identificador ou '(', encontrado ')'"),
    ("print(-2);", "1:7: esperado numero, identificador ou '(', encontrado '-'"),
    ("x = 1 < 2 < 3;", "1:11: esperado ';', encontrado '<'"),
    ("print((2 + 3);", "1:14: esperado ')', encontrado ';'"),
    ("print(x)", "1:9: esperado ';', encontrado fim da entrada"),
    ("int x = 10;", "1:7: esperado ';', encontrado '='"),
    ("5 = x;", "1:1: esperado comando ('int', 'bool', 'print', 'if', 'while', 'for', '{' ou identificador), "
               "encontrado '5'"),
    ("}", "1:1: esperado fim da entrada, encontrado '}'"),
    ("{ int x;", "1:9: esperado '}', encontrado fim da entrada"),
    ("if (1 < 2) print(1);", "1:12: esperado '{', encontrado 'print'"),
    ("for (int i; i < 3) { }", "1:18: esperado ';', encontrado ')'"),
    # dois erros: a análise para no primeiro
    ("print(2 + ); x = ;", "1:11: esperado numero, identificador ou '(', encontrado ')'"),
]


@pytest.mark.parametrize("source, message", SYNTAX_ERRORS)
def test_syntax_error(source, message):
    program, diagnostics = parse(source)
    assert program is None
    assert len(diagnostics) == 1
    assert str(diagnostics[0]) == message


def test_deep_nesting_becomes_a_diagnostic():
    program, diagnostics = parse("print(" + "(" * 1000 + "1" + ")" * 1000 + ");")
    assert program is None
    assert diagnostics[0].message == "expressao aninhada demais"


# Aula 07, slide 57: os oito casos da atividade
SLIDE_57 = [
    ("print(2 + 3 * 4);", True),
    ("print((2 + 3) * 4);", True),
    ("print(10 - 3 - 2);", True),
    ("print(2 + );", False),
    ("if (1 < 2) {}", True),
    ("if (1 < 2) {} else {}", True),
    ("if (1 < 2) print(1);", False),
    ("if (1 < 2) { if (2 < 3) {} } else {}", True),
]


@pytest.mark.parametrize("source, valid", SLIDE_57)
def test_slide_57(source, valid):
    program, _ = parse(source)
    assert (program is not None) == valid
