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


def parse(source: str):
    tokens, lexical = Lexer(source).scan_tokens()

    assert not lexical, f"{source!r} tem erro lexico: {lexical}"

    return Parser(tokens).parse()

# Etapa 2: comandos e programa, com as linhas validas da verificacao do enunciado (slide 6)
PROGRAMS = [
    ("", "Programa([])"),
    ("// so comentario\n", "Programa([])"),
    ("print(y);", "Programa([Saida(Variavel(y))])"),
    ("print(2 + 3 * 4);",
     "Programa([Saida(Binaria(+, Inteiro(2), Binaria(*, Inteiro(3), Inteiro(4))))])"),
    ("print((2 + 3) * 4);",
     "Programa([Saida(Binaria(*, Binaria(+, Inteiro(2), Inteiro(3)), Inteiro(4)))])"),
    ("print(10 - 3 - 2);",
     "Programa([Saida(Binaria(-, Binaria(-, Inteiro(10), Inteiro(3)), Inteiro(2)))])"),
    ("int x;\nx = 2 + 3 * 4;\nprint(x);",
     "Programa([Declaracao(x), Atribuicao(x, Binaria(+, Inteiro(2), Binaria(*, Inteiro(3), "
     "Inteiro(4)))), Saida(Variavel(x))])"),
    ("int valor;\nvalor = 10;\nprint(valor);",
     "Programa([Declaracao(valor), Atribuicao(valor, Inteiro(10)), Saida(Variavel(valor))])"),
    ("print(2);", "Programa([Saida(Inteiro(2))])"),
    ("print(((2)));", "Programa([Saida(Inteiro(2))])"),
    ("x = 007;", "Programa([Atribuicao(x, Inteiro(007))])"),
    ("int x; int x;", "Programa([Declaracao(x), Declaracao(x)])"),
    ("int intx; intx = intx;", "Programa([Declaracao(intx), Atribuicao(intx, Variavel(intx))])"),
]


@pytest.mark.parametrize("source, expected", PROGRAMS)
def test_program(source, expected):
    program, diagnostics = parse(source)
    assert diagnostics == []
    assert str(program) == expected


# Etapa 3: diagnosticos - (simbolo encontrado, linha, coluna) e a mensagem completa
SYNTAX_ERRORS = [
    ("print(2 + );", (")", 1, 11), "1:11: esperado numero, identificador ou '(', encontrado ')'"),
    ("print(total-);", (")", 1, 13), "1:13: esperado numero, identificador ou '(', encontrado ')'"),
    ("print();", (")", 1, 7), "1:7: esperado numero, identificador ou '(', encontrado ')'"),
    ("print(-2);", ("-", 1, 7), "1:7: esperado numero, identificador ou '(', encontrado '-'"),
    ("x = ;", (";", 1, 5), "1:5: esperado numero, identificador ou '(', encontrado ';'"),
    ("print(x;", (";", 1, 8), "1:8: esperado ')', encontrado ';'"),
    ("print((2 + 3);", (";", 1, 14), "1:14: esperado ')', encontrado ';'"),
    ("print(2 3);", ("3", 1, 9), "1:9: esperado ')', encontrado '3'"),
    ("print 2;", ("2", 1, 7), "1:7: esperado '(', encontrado '2'"),
    ("print(x)", ("", 1, 9), "1:9: esperado ';', encontrado fim da entrada"),
    ("print(x) print(y);", ("print", 1, 10), "1:10: esperado ';', encontrado 'print'"),
    ("int x", ("", 1, 6), "1:6: esperado ';', encontrado fim da entrada"),
    ("int 5;", ("5", 1, 5), "1:5: esperado identificador, encontrado '5'"),
    ("int x = 10;", ("=", 1, 7), "1:7: esperado ';', encontrado '='"),
    ("x + 1;", ("+", 1, 3), "1:3: esperado '=', encontrado '+'"),
    ("x = 1; y", ("", 1, 9), "1:9: esperado '=', encontrado fim da entrada"),
    ("x = 1 == 2;", ("==", 1, 7), "1:7: esperado ';', encontrado '=='"),
    ("5 = x;", ("5", 1, 1),
        "1:1: esperado comando ('int', 'print', 'if', 'while', 'for' ou identificador), encontrado '5'"),
    ("{ }", ("{", 1, 1),
        "1:1: esperado comando ('int', 'print', 'if', 'while', 'for' ou identificador), encontrado '{'"),
    ("print(x);)", (")", 1, 10),
        "1:10: esperado comando ('int', 'print', 'if', 'while', 'for' ou identificador), encontrado ')'"),
    ("x = 2 +\n  * 3;", ("*", 2, 3), "2:3: esperado numero, identificador ou '(', encontrado '*'"),
    ("int x;\nx = (1 + 2;\nprint(x);", (";", 2, 11), "2:11: esperado ')', encontrado ';'"),
    # Dois erros na mesma linha: so o primeiro e relatado
    ("print(2 + ); x = ;", (")", 1, 11),
     "1:11: esperado numero, identificador ou '(', encontrado ')'"),
]


@pytest.mark.parametrize("source, position, message", SYNTAX_ERRORS)
def test_syntax_error(source, position, message):
    program, diagnostics = parse(source)
    assert program is None
    assert len(diagnostics) == 1, f"{source!r} nao parou no primeiro erro: {diagnostics}"
    assert (diagnostics[0].symbol, diagnostics[0].line, diagnostics[0].column) == position
    assert str(diagnostics[0]) == message


def test_deep_nesting_becomes_a_diagnostic_instead_of_a_traceback():
    depth = 1000
    program, diagnostics = parse("print(" + "(" * depth + "1" + ")" * depth + ");")
    assert program is None
    assert len(diagnostics) == 1
    assert diagnostics[0].message == "expressao aninhada demais"
