import pytest

from ..analise.erros import ErroLexico
from ..analise.lexer import tokenizar
from ..spec.tabela import CLASSES_NUCLEO

CLASSES = {classe.nome: classe for classe in CLASSES_NUCLEO}


def e_lexema_unico(nome: str, palavra: str) -> bool:
    """Verifica se a palavra inteira e um unico lexema da classe indicada."""
    return CLASSES[nome].padrao.fullmatch(palavra) is not None


MENOR_PALAVRA_VALIDA = [
    ("ESPACO_EM_BRANCO", " "),
    ("COMENTARIO", "//"),
    ("IDENTIFICADOR_BASE", "_"),
    ("LITERAL_INTEIRO", "0"),
    ("ATRIBUICAO", "="),
    ("OPERADOR_ARITMETICO", "+"),
    ("DELIMITADOR", "("),
]

# Repeticao so se aplica as classes cuja expressao usa * ou +. ATRIBUICAO,
# OPERADOR_ARITMETICO e DELIMITADOR casam exatamente um caractere.
UMA_REPETICAO = [
    ("ESPACO_EM_BRANCO", " "),
    ("COMENTARIO", "//x"),
    ("IDENTIFICADOR_BASE", "A1"),
    ("LITERAL_INTEIRO", "4"),
]

VARIAS_REPETICOES = [
    ("ESPACO_EM_BRANCO", " \t\n"),
    ("COMENTARIO", "// comentario"),
    ("IDENTIFICADOR_BASE", "total2"),
    ("LITERAL_INTEIRO", "45"),
]

FORA_DO_ALFABETO = [
    ("tot@l", 3),
    ("a#b", 1),
    ("valor $ 2", 6),
    ("%", 0),
]


def test_menor_palavra_valida():
    """Cada classe aceita a menor palavra que sua expressao formal permite."""
    for nome, palavra in MENOR_PALAVRA_VALIDA:
        assert e_lexema_unico(nome, palavra), f"{nome} rejeitou {palavra!r}"


def test_palavra_vazia_rejeitada():
    """Se alguma classe aceitasse a palavra vazia, o cursor do lexer nao avancaria."""
    for classe in CLASSES_NUCLEO:
        assert classe.padrao.fullmatch("") is None, classe.nome


def test_uma_repeticao():
    """Classes com * ou + aceitam exatamente uma repeticao do corpo."""
    for nome, palavra in UMA_REPETICAO:
        assert e_lexema_unico(nome, palavra), f"{nome} rejeitou {palavra!r}"


def test_varias_repeticoes():
    """As mesmas classes aceitam varias repeticoes do corpo."""
    for nome, palavra in VARIAS_REPETICOES:
        assert e_lexema_unico(nome, palavra), f"{nome} rejeitou {palavra!r}"


def test_simbolo_fora_do_alfabeto():
    """Simbolo fora do alfabeto-fonte levanta ErroLexico na posicao exata."""
    for fonte, pos in FORA_DO_ALFABETO:
        with pytest.raises(ErroLexico) as erro:
            tokenizar(fonte)
        assert erro.value.pos == pos, f"{fonte!r} apontou {erro.value.pos}"
