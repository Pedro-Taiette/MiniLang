import pytest

from ..analise.lexer import tokenizar
from ..analise.erros import ErroLexico

def test_single_identifier():
    """Tem que ficar o mesmo tamanho e o lexema ser o que era antes."""
    tokens = tokenizar("t")
    assert len(tokens) == 1
    assert tokens[0].lexema == "t"

def test_empty_string_produces_no_tokens():
    """Fonte vazia e um programa valido de zero tokens, nao um erro lexico."""
    assert tokenizar("") == []

def test_keywords():
    """Testa as KW 'int' e 'print' e ve se estão com o value correto."""
    tokens = tokenizar("int print")
    assert len(tokens) == 2
    assert tokens[0].tipo.value == "KW_INT"
    assert tokens[1].tipo.value == "KW_PRINT"

def test_keyword_prefix_is_identifier():
    """So o lexema inteiro vira palavra reservada: 'intx' e um IDENT unico."""
    tokens = tokenizar("intx printer")
    assert [t.tipo.value for t in tokens] == ["IDENT", "IDENT"]
    assert [t.lexema for t in tokens] == ["intx", "printer"]

def test_assignment():
    """Testa os tipos de uma expressão."""
    tokens = tokenizar("x = 5")
    types = [t.tipo.value for t in tokens]
    assert types == ["IDENT", "ASSIGN", "INT_LITERAL"]

def test_token_positions():
    """A pos de cada token e o indice do inicio do lexema na fonte."""
    tokens = tokenizar("x = 50")
    assert [t.pos for t in tokens] == [0, 2, 4]

def test_arithmetic():
    """Testa os tipos de aritmética complexa."""
    tokens = tokenizar("a + b - c * d / e")
    assert len(tokens) == 9
    assert tokens[1].tipo.value == "PLUS"
    assert tokens[3].tipo.value == "MINUS"
    assert tokens[5].tipo.value == "STAR"
    assert tokens[7].tipo.value == "SLASH"

def test_slash_vence_comentario_por_tamanho():
    """Conflito de prefixo: '/' e SLASH, '//' inicia comentario (maior lexema)."""
    assert [t.tipo.value for t in tokenizar("a / b")] == ["IDENT", "SLASH", "IDENT"]
    assert [t.tipo.value for t in tokenizar("a // b")] == ["IDENT"]

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
    with pytest.raises(ErroLexico) as erro:
        tokenizar("á")
    assert "fora do alfabeto-fonte" in str(erro.value)
    assert erro.value.caractere == "á"
    assert erro.value.pos == 0

def test_invalid_character_reports_position():
    """O erro aponta o indice exato do caractere invalido no meio da fonte."""
    with pytest.raises(ErroLexico) as erro:
        tokenizar("total = 1 $ 2")
    assert erro.value.pos == 10
