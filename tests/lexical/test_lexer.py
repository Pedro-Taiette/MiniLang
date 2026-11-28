import pytest

from minilang.compiler.common.diagnostics import Phase
from minilang.compiler.lexical.lexer import Lexer
from minilang.compiler.lexical.tokens import TokenType


def scan(source: str):
    tokens, diagnostics = Lexer(source).scan_tokens()
    return tokens, [(d.lexeme, d.line, d.column) for d in diagnostics]


TOKENIZATION = [
    # palavras reservadas e identificadores
    ("int bool print if else while for", "KW_INT KW_BOOL KW_PRINT KW_IF KW_ELSE KW_WHILE KW_FOR EOF"),
    ("true false", "BOOL_LITERAL BOOL_LITERAL EOF"),
    ("AND OR", "AND OR EOF"),
    ("int intx ifx while", "KW_INT IDENT IDENT KW_WHILE EOF"),
    ("print2 else2 while1", "IDENT IDENT IDENT EOF"),
    ("ANDx trueValue ORa falsey", "IDENT IDENT IDENT IDENT EOF"),
    ("and or True Int IF", "IDENT IDENT IDENT IDENT IDENT EOF"),
    ("_ _a a_1 A1", "IDENT IDENT IDENT IDENT EOF"),
    ("while1 != while", "IDENT BANG_EQUAL KW_WHILE EOF"),

    # numeros: o sinal é um token separado
    ("0 7 45 007", "INT_LITERAL INT_LITERAL INT_LITERAL INT_LITERAL EOF"),
    ("007 -10 +7", "INT_LITERAL MINUS INT_LITERAL PLUS INT_LITERAL EOF"),
    ("2total total-2", "INT_LITERAL IDENT IDENT MINUS INT_LITERAL EOF"),
    ("2if <= 03", "INT_LITERAL KW_IF LESS_EQUAL INT_LITERAL EOF"),

    # operadores: o maior lexema vence
    ("+ - * /", "PLUS MINUS STAR SLASH EOF"),
    ("< <= > >= == !=", "LESS LESS_EQUAL GREATER GREATER_EQUAL EQUAL_EQUAL BANG_EQUAL EOF"),
    ("= == ===", "ASSIGN EQUAL_EQUAL EQUAL_EQUAL ASSIGN EOF"),
    ("!= ! <==", "BANG_EQUAL LESS_EQUAL ASSIGN EOF"),
    ("intx===007;", "IDENT EQUAL_EQUAL ASSIGN INT_LITERAL SEMICOLON EOF"),
    ("a/b", "IDENT SLASH IDENT EOF"),

    # delimitadores encostados sao lexemas separados
    ("(){});", "LPAREN RPAREN LBRACE RBRACE RPAREN SEMICOLON EOF"),
    ("{print(x);}", "LBRACE KW_PRINT LPAREN IDENT RPAREN SEMICOLON RBRACE EOF"),

    # comentarios e espaços somem
    ("", "EOF"),
    ("//", "EOF"),
    ("///x", "EOF"),
    ("// comentário com acentuação", "EOF"),
    ("x=1 // fim", "IDENT ASSIGN INT_LITERAL EOF"),
    ("int\tx;", "KW_INT IDENT SEMICOLON EOF"),
    ("intx==10//fim", "IDENT EQUAL_EQUAL INT_LITERAL EOF"),
    ("print(total-2); // ok", "KW_PRINT LPAREN IDENT MINUS INT_LITERAL RPAREN SEMICOLON EOF"),

    ("if(total2>=10){print(total2);}",
     "KW_IF LPAREN IDENT GREATER_EQUAL INT_LITERAL RPAREN LBRACE KW_PRINT LPAREN "
     "IDENT RPAREN SEMICOLON RBRACE EOF"),
    ("while (ativo AND (n > 0)) {",
     "KW_WHILE LPAREN IDENT AND LPAREN IDENT GREATER INT_LITERAL RPAREN RPAREN LBRACE EOF"),
]

POSITIONS = [
    ("int\n  valor", "KW_INT@1:1 IDENT@2:3 EOF@2:8"),
    ("@x", "IDENT@1:2 EOF@1:3"),
    ("// comentario\n  while", "KW_WHILE@2:3 EOF@2:8"),
    ("a//x\n  >==b", "IDENT@1:1 GREATER_EQUAL@2:3 ASSIGN@2:5 IDENT@2:6 EOF@2:7"),
    ("int x;\nif(x<10){\n  print(x);\n}",
     "KW_INT@1:1 IDENT@1:5 SEMICOLON@1:6 KW_IF@2:1 LPAREN@2:3 IDENT@2:4 LESS@2:5 "
     "INT_LITERAL@2:6 RPAREN@2:8 LBRACE@2:9 KW_PRINT@3:3 LPAREN@3:8 IDENT@3:9 "
     "RPAREN@3:10 SEMICOLON@3:11 RBRACE@4:1 EOF@4:2"),
    ("vãlor", "IDENT@1:1 IDENT@1:3 EOF@1:6"),

    # TAB avança uma coluna so
    ("\tprint", "KW_PRINT@1:2 EOF@1:7"),
    ("a\t\tb", "IDENT@1:1 IDENT@1:4 EOF@1:5"),

    # CRLF conta uma quebra, CR ou NL sozinhos tambem
    ("int\r\nx", "KW_INT@1:1 IDENT@2:1 EOF@2:2"),
    ("a\rb", "IDENT@1:1 IDENT@2:1 EOF@2:2"),
    ("a\r\n\r\nb", "IDENT@1:1 IDENT@3:1 EOF@3:2"),
    ("a\n\rb", "IDENT@1:1 IDENT@3:1 EOF@3:2"),
    ("x;\r\n", "IDENT@1:1 SEMICOLON@1:2 EOF@2:1"),
    ("// fim\r\nx", "IDENT@2:1 EOF@2:2"),
]

DIAGNOSTICS = [
    ("@x", [("@", 1, 1)]),
    ("!= ! <==", [("!", 1, 4)]),
    ("! @ !=", [("!", 1, 1), ("@", 1, 3)]),
    ("vãlor", [("ã", 1, 2)]),
    ("a % b", [("%", 1, 3)]),
    ("x := 1;", [(":", 1, 3)]),
    ("@@@", [("@", 1, 1), ("@", 1, 2), ("@", 1, 3)]),
    ("int x;\r\n  #", [("#", 2, 3)]),
    ("int intx ifx while", []),
    ("// @ ! # dentro de comentario nao conta", []),
]


@pytest.mark.parametrize("source, expected", TOKENIZATION)
def test_tokenization(source, expected):
    tokens, _ = scan(source)
    assert " ".join(token.type.value for token in tokens) == expected


@pytest.mark.parametrize("source, expected", POSITIONS)
def test_positions(source, expected):
    tokens, _ = scan(source)
    assert " ".join(f"{t.type.value}@{t.line}:{t.column}" for t in tokens) == expected


@pytest.mark.parametrize("source, expected", DIAGNOSTICS)
def test_diagnostics(source, expected):
    _, diagnostics = scan(source)
    assert diagnostics == expected


def test_diagnostic_carries_the_lexical_phase():
    _, diagnostics = Lexer("@").scan_tokens()
    assert diagnostics[0].phase is Phase.LEXICAL


def test_scan_continues_after_an_invalid_symbol():
    tokens, diagnostics = scan("int v@lor;")
    assert [t.lexeme for t in tokens] == ["int", "v", "lor", ";", ""]
    assert diagnostics == [("@", 1, 6)]


def test_empty_source_is_only_eof_at_1_1():
    tokens, diagnostics = scan("")
    assert [(t.type, t.lexeme, t.line, t.column) for t in tokens] == [
        (TokenType.EOF, "", 1, 1)
    ]
    assert diagnostics == []


def test_assignment_example_3_2():
    """A sequencia de tokens da seção 3.2 do enunciado, no mesmo formato"""
    tokens, diagnostics = scan("int x;\nx = 2 + 3 * 4;\nprint(x);\n")

    assert diagnostics == []
    assert [str(token) for token in tokens] == [
        'KW_INT("int") 1:1', 'IDENT("x") 1:5', 'SEMICOLON(";") 1:6',
        'IDENT("x") 2:1', 'ASSIGN("=") 2:3', 'INT_LITERAL("2") 2:5',
        'PLUS("+") 2:7', 'INT_LITERAL("3") 2:9', 'STAR("*") 2:11',
        'INT_LITERAL("4") 2:13', 'SEMICOLON(";") 2:14',
        'KW_PRINT("print") 3:1', 'LPAREN("(") 3:6',
        'IDENT("x") 3:7', 'RPAREN(")") 3:8', 'SEMICOLON(";") 3:9',
        'EOF("") 4:1',
    ]
