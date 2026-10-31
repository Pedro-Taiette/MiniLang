import pytest
from minilang.analysis.parser import Parser, ParseError
from minilang.spec.tokens import Token, TokenType
from minilang.analysis.lexer import Lexer

def test_advance_no_eof_devolve_eof_e_nao_move_cursor():
    tokens = [Token(TokenType.EOF, "", 1, 1)]
    parser = Parser(tokens)
    
    primeiro = parser.advance()
    assert primeiro.type is TokenType.EOF
    assert parser.current == 0
    
    segundo = parser.advance()
    assert segundo.type is TokenType.EOF
    assert parser.current == 0

def test_expect_com_tipo_errado_levanta_parse_error():
    tokens = [Token(TokenType.IDENT, "x", 1, 1), Token(TokenType.EOF, "", 1, 2)]
    parser = Parser(tokens)
    
    with pytest.raises(ParseError) as exc_info:
        parser.expect(TokenType.SEMICOLON, "';'")
        
    diagnostic = exc_info.value.diagnostic
    assert diagnostic.line == 1
    assert diagnostic.column == 1
    assert diagnostic.message == "esperado ';', encontrado 'x'"

def test_match_sem_casar_nao_consome():
    tokens = [Token(TokenType.IDENT, "x", 1, 1), Token(TokenType.EOF, "", 1, 2)]
    parser = Parser(tokens)
    
    casou = parser.match(TokenType.PLUS, TokenType.MINUS)
    
    assert not casou
    assert parser.current == 0
    assert parser.peek().type is TokenType.IDENT

EXPRESSIONS = [
    ("2 + 3 * 4", "Binaria(+, Inteiro(2), Binaria(*, Inteiro(3), Inteiro(4)))"),
    ("(2 + 3) * 4", "Binaria(*, Binaria(+, Inteiro(2), Inteiro(3)), Inteiro(4))"),
    ("10 - 3 - 2", "Binaria(-, Binaria(-, Inteiro(10), Inteiro(3)), Inteiro(2))"),
    ("8 / 4 / 2", "Binaria(/, Binaria(/, Inteiro(8), Inteiro(4)), Inteiro(2))"),
    ("2 - 3 + 4", "Binaria(+, Binaria(-, Inteiro(2), Inteiro(3)), Inteiro(4))"),
    ("2 * 3 + 4", "Binaria(+, Binaria(*, Inteiro(2), Inteiro(3)), Inteiro(4))"),
    ("8 / 2 * 3", "Binaria(*, Binaria(/, Inteiro(8), Inteiro(2)), Inteiro(3))"),
    ("total-2", "Binaria(-, Variavel(total), Inteiro(2))"),
    ("saldo + 10 - desconto",
     "Binaria(-, Binaria(+, Variavel(saldo), Inteiro(10)), Variavel(desconto))"),
    ("a * (b - c) / d",
     "Binaria(/, Binaria(*, Variavel(a), Binaria(-, Variavel(b), Variavel(c))), Variavel(d))"),
    ("((x))", "Variavel(x)"),
    ("007", "Inteiro(007)"),
]


def parse_expression(source: str) -> str:
    tokens, _ = Lexer(source).scan_tokens()
    parser = Parser(tokens)
    node = parser.expression()
    assert parser.at_end(), f"{source!r}: sobrou {parser.peek()}"
    return str(node)


@pytest.mark.parametrize("source, expected", EXPRESSIONS)
def test_expression(source, expected):
    assert parse_expression(source) == expected