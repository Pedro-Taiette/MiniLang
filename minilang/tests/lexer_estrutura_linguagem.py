from ..analise.lexer import tokenizar
from ..analise.erros import ErroLexico

def test_single_identifier():
    """Tem que ficar o mesmo tamanho e o lexema ser o que era antes."""
    tokens = tokenizar("t")
    assert len(tokens) == 1
    assert tokens[0].lexema == "t"

def test_empty_string_raises_error():
    """Passar uma string vazia deve levantar um ErroLexico."""
    try:
        tokenizar("")
        assert False, "Deveria ter levantado ErroLexico."
    except ErroLexico:
        pass

def test_keywords():
    """Testa as KW 'int' e 'print' e ve se estão com o value correto."""
    tokens = tokenizar("int print")
    assert len(tokens) == 2
    assert tokens[0].tipo.value == "KW_INT"
    assert tokens[1].tipo.value == "KW_PRINT"

def test_assignment():
    """Testa os tipos de uma expressão."""
    tokens = tokenizar("x = 5")
    types = [t.tipo.value for t in tokens]
    assert types == ["IDENT", "ASSIGN", "INT_LITERAL"]

def test_arithmetic():
    """Testa os tipos de aritmética complexa."""
    tokens = tokenizar("a + b - c * d / e")
    assert len(tokens) == 9
    assert tokens[1].tipo.value == "PLUS"
    assert tokens[3].tipo.value == "MINUS"
    assert tokens[5].tipo.value == "STAR"
    assert tokens[7].tipo.value == "SLASH"

def test_whitespace_ignored():
    """Vendo se os espaços foram ignorados."""
    tokens = tokenizar("x   =   5")
    assert len(tokens) == 3

def test_whitespace_and_comment_not_ignored():
    """A gente tem como ativar e desativar o ignore, aq a gente desativa ele para ver os tokens"""
    tokens = tokenizar("x = 5 // esse e comentario", True)
    assert len(tokens) == 7
    assert tokens[1].tipo.value == "WHITESPACE"
    assert tokens[6].tipo.value == "LINE_COMMENT"

def test_comments_is_single_token():
    """Testa se o comentário é um token só."""
    tokens = tokenizar("x=5// esse e comentario", True)
    assert len(tokens) == 4
    assert tokens[3].tipo.value == "LINE_COMMENT"

def test_invalid_character_raises_error():
    """Testa se letras fora do alfabeto estão levantando ErroLexico."""
    try:
        tokenizar("á")
        assert False, "Deveria ter levantado ErroLexico."
    except ErroLexico as e:
        assert "fora do alfabeto-fonte" in str(e)