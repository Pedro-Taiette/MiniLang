from ..spec.tabela import CLASSES_NUCLEO, Acao, ClasseLexica
from ..spec.tokens import Token
from .erros import ErroLexico


def tokenizar(fonte: str, incluir_ignorados: bool = False) -> list[Token]:

    tokens: list[Token] = []
    pos = 0

    while pos < len(fonte):
        classe, lexema = _maior_lexema(fonte, pos)

        if incluir_ignorados or classe.acao is Acao.EMITE:
            tokens.append(Token(classe.tipo_de(lexema), lexema, pos))

        pos += len(lexema)

    return tokens


def _maior_lexema(fonte: str, pos: int) -> tuple[ClasseLexica, str]:

    classe_vencedora, lexema_vencedor = None, ""

    for classe in CLASSES_NUCLEO:
        casamento = classe.padrao.match(fonte, pos)

        # Vence o maior lexema - caso  empate, a classe declarada primeiro
        if casamento and len(casamento.group()) > len(lexema_vencedor):
            classe_vencedora, lexema_vencedor = classe, casamento.group()

    if classe_vencedora is None:
        raise ErroLexico(fonte[pos], pos)
    
    return classe_vencedora, lexema_vencedor
