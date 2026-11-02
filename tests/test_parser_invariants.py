import pytest

from minilang.analysis.lexer import Lexer
from minilang.analysis.parser import Parser

from .test_parser import PROGRAMS, SYNTAX_ERRORS

SOURCES = [
    "",
    ";;;",
    "(((",
    ")))",
    "int",
    "print",
    "x",
    "=",
    "print(",
    "int x;;",
    "x = x = x;",
    "x = 1 2;",
    *(source for source, _ in PROGRAMS),
    *(source for source, _, _ in SYNTAX_ERRORS),
]


def run(source: str):
    tokens, _ = Lexer(source).scan_tokens()
    parser = Parser(tokens)
    return parser, tokens, parser.parse()


@pytest.mark.parametrize("source", SOURCES)
def test_result_is_a_program_or_exactly_one_diagnostic(source):
    """parse() nunca levanta: ou devolve a AST sem diagnosticos, ou None e um diagnostico so"""
    _, _, (program, diagnostics) = run(source)
    if program is not None:
        assert diagnostics == []
    else:
        assert len(diagnostics) == 1


@pytest.mark.parametrize("source", SOURCES)
def test_success_consumes_every_token(source):
    parser, tokens, (program, _) = run(source)
    if program is not None:
        assert parser.at_end()
        assert parser.current == len(tokens) - 1


@pytest.mark.parametrize("source", SOURCES)
def test_diagnostic_points_at_the_token_under_the_cursor(source):
    parser, _, (program, diagnostics) = run(source)
    if program is None:
        found = parser.peek()
        assert (diagnostics[0].symbol, diagnostics[0].line, diagnostics[0].column) == (
            found.lexeme, found.line, found.column
        )


@pytest.mark.parametrize("source", SOURCES)
def test_parser_does_not_change_the_token_list(source):
    tokens, _ = Lexer(source).scan_tokens()
    before = list(tokens)
    Parser(tokens).parse()
    assert tokens == before


def test_advance_keeps_returning_the_same_eof():
    tokens, _ = Lexer("int x;").scan_tokens()
    parser = Parser(tokens)
    parser.parse()
    assert parser.advance() is parser.advance() is tokens[-1]


SAME_TREE = [
    ("print(2 + 3 * 4);", "print(2 + (3 * 4));"),
    ("print(10 - 3 - 2);", "print((10 - 3) - 2);"),
    ("print(8 / 4 / 2);", "print((8 / 4) / 2);"),
    ("x=1;", "x = 1 ; // c"),
    ("int x;print(x);", "int x;\r\n\r\nprint( x );\r\n"),
]


@pytest.mark.parametrize("source, equivalent", SAME_TREE)
def test_redundant_parentheses_spaces_and_comments_keep_the_tree(source, equivalent):
    _, _, (program, _) = run(source)
    _, _, (other, _) = run(equivalent)
    assert program is not None
    assert str(program) == str(other)
