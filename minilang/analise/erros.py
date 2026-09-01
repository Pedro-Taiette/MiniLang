from ..spec.alfabeto import ALFABETO_FONTE


class ErroLexico(Exception):

    def __init__(self, caractere: str, pos: int) -> None:
        self.caractere = caractere
        self.pos = pos
        motivo = (
            "fora do alfabeto-fonte"
            if caractere not in ALFABETO_FONTE
            else "nao casa com nenhuma classe da tabela"
        )
        
        super().__init__(f"posicao {pos}: {caractere!r} {motivo}")
