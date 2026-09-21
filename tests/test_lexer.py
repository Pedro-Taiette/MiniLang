import pytest

from minilang.analysis.lexer import Lexer
from minilang.spec.tokens import TokenType


def scan(source: str):
    tokens, diagnostics = Lexer(source).scan_tokens()
    return tokens, [(d.symbol, d.line, d.column) for d in diagnostics]


# 4.1 Tokenizacao e 6 Verificacao individual
TOKENIZATION = [
    ("int intx ifx while", "KW_INT IDENT IDENT KW_WHILE EOF"),
    ("007 -10 +7", "INT_LITERAL MINUS INT_LITERAL PLUS INT_LITERAL EOF"),
    ("2total total-2", "INT_LITERAL IDENT IDENT MINUS INT_LITERAL EOF"),
    ("= == ===", "ASSIGN EQUAL_EQUAL EQUAL_EQUAL ASSIGN EOF"),
    ("!= ! <==", "BANG_EQUAL LESS_EQUAL ASSIGN EOF"),
    ("a/b", "IDENT SLASH IDENT EOF"),
    ("//", "EOF"),
    ("///x", "EOF"),
    ("{print(x);}", "LBRACE KW_PRINT LPAREN IDENT RPAREN SEMICOLON RBRACE EOF"),
    ("", "EOF"),
    ("if(total2>=10){print(total2);}",
     "KW_IF LPAREN IDENT GREATER_EQUAL INT_LITERAL RPAREN LBRACE KW_PRINT LPAREN "
     "IDENT RPAREN SEMICOLON RBRACE EOF"),
    ("intx===007;", "IDENT EQUAL_EQUAL ASSIGN INT_LITERAL SEMICOLON EOF"),
    ("while1 != while", "IDENT BANG_EQUAL KW_WHILE EOF"),
    ("2if <= 03", "INT_LITERAL KW_IF LESS_EQUAL INT_LITERAL EOF"),
]

# 4.2 Posicoes, mais os casos de posicao da secao 6
POSITIONS = [
    ("int\n  valor", "KW_INT@1:1 IDENT@2:3 EOF@2:8"),
    ("@x", "IDENT@1:2 EOF@1:3"),
    ("// comentario\n  while", "KW_WHILE@2:3 EOF@2:8"),
    ("a//x\n  >==b", "IDENT@1:1 GREATER_EQUAL@2:3 ASSIGN@2:5 IDENT@2:6 EOF@2:7"),
    ("int x;\nif(x<10){\n  print(x);\n}",
     "KW_INT@1:1 IDENT@1:5 SEMICOLON@1:6 KW_IF@2:1 LPAREN@2:3 IDENT@2:4 LESS@2:5 "
     "INT_LITERAL@2:6 RPAREN@2:8 LBRACE@2:9 KW_PRINT@3:3 LPAREN@3:8 IDENT@3:9 "
     "RPAREN@3:10 SEMICOLON@3:11 RBRACE@4:1 EOF@4:2"),
    ("\tprint", "KW_PRINT@1:2 EOF@1:7"),
    ("vãlor", "IDENT@1:1 IDENT@1:3 EOF@1:6"),
]

DIAGNOSTICS = [
    ("@x", [("@", 1, 1)]),
    ("!= ! <==", [("!", 1, 4)]),
    ("! @ !=", [("!", 1, 1), ("@", 1, 3)]),
    ("vãlor", [("ã", 1, 2)]),
    ("int intx ifx while", []),
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


def test_empty_source_is_only_eof_at_1_1():
    tokens, diagnostics = scan("")
    assert [(t.type, t.lexeme, t.line, t.column) for t in tokens] == [
        (TokenType.EOF, "", 1, 1)
    ]
    assert diagnostics == []
