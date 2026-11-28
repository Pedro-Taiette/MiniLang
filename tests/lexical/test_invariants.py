import pytest

from minilang.compiler.lexical.lexer import Lexer
from minilang.compiler.lexical.tokens import KEYWORDS, SYMBOLS, TokenType

SOURCES = [
    "",
    "   ",
    "//",
    "@@@",
    "!!!",
    "int x;",
    "{print(x);} // fim",
    "a\rb",
    "int x;\r\nprint(x);\r\n",
    "v@lor = 007;\n! @ !=",
]


@pytest.mark.parametrize("source", SOURCES)
def test_exactly_one_eof_and_it_is_last(source):
    tokens, _ = Lexer(source).scan_tokens()
    assert [t.type for t in tokens].count(TokenType.EOF) == 1
    assert tokens[-1].type is TokenType.EOF
    assert tokens[-1].lexeme == ""


@pytest.mark.parametrize("source", SOURCES)
def test_every_iteration_consumes_at_least_one_symbol(source):
    """A invariante que evita laco infinito em entrada invalida"""
    lexer = Lexer(source)
    while not lexer.at_end():
        before = lexer.current
        lexer.start = lexer.current
        lexer.start_line = lexer.line
        lexer.start_column = lexer.column

        lexer.scan_token()

        assert lexer.current > before, f"{source!r} travou em {before}"


def test_crlf_counts_as_a_single_line_break():
    windows, _ = Lexer("int\r\nx").scan_tokens()
    unix, _ = Lexer("int\nx").scan_tokens()
    assert [(t.type, t.line, t.column) for t in windows] == [
        (t.type, t.line, t.column) for t in unix
    ]


def test_eof_sits_right_after_the_last_symbol():
    tokens, _ = Lexer("abc").scan_tokens()
    assert (tokens[-1].line, tokens[-1].column) == (1, 4)


@pytest.mark.parametrize("lexeme, token_type", list(KEYWORDS.items()) + list(SYMBOLS.items()))
def test_every_keyword_and_symbol_scans_as_its_own_type(lexeme, token_type):
    """Amarra as duas tabelas ao lexer: cada entrada sai sozinha, como um token do tipo prometido"""
    tokens, diagnostics = Lexer(lexeme).scan_tokens()

    assert diagnostics == []
    assert [(t.type, t.lexeme) for t in tokens] == [(token_type, lexeme), (TokenType.EOF, "")]
