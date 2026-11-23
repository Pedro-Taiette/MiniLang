"""Invariantes do parser: o que vale para qualquer entrada, válida ou não"""

import pytest

from minilang.analysis.parser import Parser

from .support import compact, parse, tokenize
from .test_parser import PROGRAMS, SYNTAX_ERRORS

# Entradas soltas, mais todas as que o test_parser já usa
SOURCES = [";;;", "(((", "{{{", "int", "print(", "x = x = x;"]
for case in PROGRAMS + SYNTAX_ERRORS:
    SOURCES.append(case[0])


@pytest.mark.parametrize("source", SOURCES)
def test_result_is_a_program_or_exactly_one_diagnostic(source):
    """parse() nunca levanta: ou devolve a AST e consome tudo, ou None e um diagnostico no token encontrado"""
    tokens = tokenize(source)
    parser = Parser(tokens)
    program, diagnostics = parser.parse()

    if program is not None:
        assert diagnostics == []
        assert parser.current == len(tokens) - 1        # só sobrou o EOF
    else:
        assert len(diagnostics) == 1
        assert diagnostics[0].line == parser.peek().line
        assert diagnostics[0].column == parser.peek().column


def test_redundant_parentheses_spaces_and_comments_keep_the_tree():
    program, _ = parse("x = 10 - 3 - 2;")
    other, _ = parse("x = ((10 - 3) - 2) ; // comentario\r\n")
    assert compact(program) == compact(other)
