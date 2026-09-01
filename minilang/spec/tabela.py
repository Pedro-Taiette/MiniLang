# Tabela lexical da MiniLang-Core: uma linha por classe, com os campos do slide 88.
# A tabela e dado. O lexer a percorre sem saber o que cada classe significa.

import re
from dataclasses import dataclass, field
from enum import Enum

from .tokens import TokenType


class Acao(Enum):
    EMITE = "emitido ao parser"
    IGNORA = "reconhecido e ignorado"


@dataclass(frozen=True)
class ClasseLexica:
    nome: str
    regex: str
    acao: Acao

    tipo: TokenType | None = None
    tipo_por_lexema: dict[str, TokenType] = field(default_factory=dict)

    descricao: str = ""
    conjuntos: str = ""
    expressao_formal: str = ""
    justificativa: str = ""

    @property
    def padrao(self) -> re.Pattern:
        return re.compile(self.regex)

    def tipo_de(self, lexema: str) -> TokenType:
        tipo = self.tipo_por_lexema.get(lexema, self.tipo)
        if tipo is None:
            raise KeyError(f"{self.nome} nao classifica {lexema!r}")
        return tipo


PALAVRAS_RESERVADAS: dict[str, TokenType] = {
    "int": TokenType.KW_INT,
    "print": TokenType.KW_PRINT,
}


# A ordem so desempata padroes que casem o MESMO numero de caracteres. Conflitos
# de prefixo ("/" vs "//", "=" vs "==") sao resolvidos pelo tamanho do lexema.
CLASSES_NUCLEO: list[ClasseLexica] = [
    ClasseLexica(
        nome="ESPACO_EM_BRANCO",
        regex=r"[ \t\r\n]+",
        acao=Acao.IGNORA,
        tipo=TokenType.WHITESPACE,
        descricao="Um ou mais espacos, tabulacoes ou quebras de linha.",
        conjuntos="ESPACOS_EM_BRANCO",
        expressao_formal="EspacosEmBranco+",
        justificativa="Separa lexemas adjacentes. Exige ao menos um caractere.",
    ),
    ClasseLexica(
        nome="COMENTARIO",
        regex=r"//[^\r\n]*",
        acao=Acao.IGNORA,
        tipo=TokenType.LINE_COMMENT,
        descricao="Comeca com // e segue ate imediatamente antes da quebra de linha.",
        conjuntos="CORPO_COMENTARIO",
        expressao_formal='"//" CorpoComentario*',
        justificativa="Corpo vazio e valido. A quebra encerra, mas nao integra o lexema.",
    ),
    ClasseLexica(
        nome="IDENTIFICADOR_BASE",
        regex=r"[A-Za-z_][A-Za-z0-9_]*",
        acao=Acao.EMITE,
        tipo=TokenType.IDENT,
        tipo_por_lexema=PALAVRAS_RESERVADAS,
        descricao="Letra ou sublinhado, seguido de letras, digitos ou sublinhados.",
        conjuntos="INICIO_IDENTIFICADOR, RESTO_IDENTIFICADOR",
        expressao_formal="InicioIdentificador RestoIdentificador*",
        justificativa="Classe-base: int e print tambem casam aqui e sao separados depois.",
    ),
    ClasseLexica(
        nome="LITERAL_INTEIRO",
        regex=r"[0-9]+",
        acao=Acao.EMITE,
        tipo=TokenType.INT_LITERAL,
        descricao="Um ou mais digitos.",
        conjuntos="DIGITOS",
        expressao_formal="Digitos+",
        justificativa="O sinal fica de fora: -10 e a sequencia MINUS INT_LITERAL.",
    ),
    ClasseLexica(
        nome="ATRIBUICAO",
        regex=r"=",
        acao=Acao.EMITE,
        tipo=TokenType.ASSIGN,
        descricao="O simbolo de atribuicao.",
        conjuntos="-",
        expressao_formal='"="',
        justificativa='"=" e atribuicao; "==" e extensao e casa um lexema mais longo.',
    ),
    ClasseLexica(
        nome="OPERADOR_ARITMETICO",
        regex=r"[-+*/]",
        acao=Acao.EMITE,
        tipo_por_lexema={
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
        },
        descricao="Um dos quatro operadores aritmeticos.",
        conjuntos="-",
        expressao_formal='"+" u "-" u "*" u "/"',
        justificativa="Familia que gera PLUS, MINUS, STAR e SLASH.",
    ),
    ClasseLexica(
        nome="DELIMITADOR",
        regex=r"[();]",
        acao=Acao.EMITE,
        tipo_por_lexema={
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ";": TokenType.SEMICOLON,
        },
        descricao="Parenteses de abertura, de fechamento ou ponto e virgula.",
        conjuntos="-",
        expressao_formal='"(" u ")" u ";"',
        justificativa="Cada delimitador e um lexema isolado: () sao dois tokens.",
    ),
]
