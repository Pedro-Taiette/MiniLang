import pytest

from minilang.analysis.lexer import Lexer
from minilang.spec.lexical_class import Action
from minilang.spec.table import LEXICAL_TABLE
from minilang.spec.tokens import TokenType

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
def test_comments_and_whitespace_never_reach_the_token_list(source):
    tokens, _ = Lexer(source).scan_tokens()
    assert not {t.type.name for t in tokens} & {"WHITESPACE", "LINE_COMMENT"}


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
    """O codigobase normaliza CRLF para um unico NL"""
    windows, _ = Lexer("int\r\nx").scan_tokens()
    unix, _ = Lexer("int\nx").scan_tokens()
    assert [(t.type, t.line, t.column) for t in windows] == [
        (t.type, t.line, t.column) for t in unix
    ]


def test_eof_sits_right_after_the_last_symbol():
    tokens, _ = Lexer("abc").scan_tokens()
    assert (tokens[-1].line, tokens[-1].column) == (1, 4)


@pytest.mark.parametrize("lexical_class", LEXICAL_TABLE, ids=lambda c: c.name)
def test_example_scans_as_its_own_class(lexical_class):
    """Amarra a tabela ao lexer: o exemplo sai como a classe promete"""
    expected = (
        set(lexical_class.type_by_lexeme.values())
        if lexical_class.type_by_lexeme
        else {lexical_class.type}
    )

    for example in lexical_class.examples:
        tokens, diagnostics = Lexer(example).scan_tokens()
        emitted = [t for t in tokens if t.type is not TokenType.EOF]

        assert not diagnostics, f"{lexical_class.name} com {example!r} gerou diagnostico"

        if lexical_class.action is Action.IGNORES:
            assert not emitted, f"{lexical_class.name} com {example!r} emitiu {emitted}"
        else:
            assert len(emitted) == 1, f"{lexical_class.name} com {example!r} -> {emitted}"
            assert emitted[0].type in expected, (
                f"{lexical_class.name} promete {expected}, lexer deu {emitted[0].type}"
            )
