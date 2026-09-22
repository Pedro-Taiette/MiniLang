"""Suite de interacoes entre classes: os oito blocos do slide 98 - Aula 03"""

from dataclasses import dataclass
from enum import Enum


class Block(Enum):
    KEYWORD_CORE_X_IDENT_BASE = "KEYWORD_CORE x IDENT_BASE"
    KEYWORD_EXT_X_IDENT_BASE = "KEYWORD_EXT x IDENT_BASE"
    ASSIGN_X_REL_OP = "ASSIGN x REL_OP"
    ARITH_OP_X_LINE_COMMENT = "ARITH_OP x LINE_COMMENT"
    REL_OP_PREFIXES = "Prefixos de REL_OP"
    ARITH_OP_X_INT_LITERAL = "ARITH_OP x INT_LITERAL"
    ADJACENT_DELIMITERS = "Delimitadores adjacentes"
    SKIPPED_CLASSES = "Classes ignoradas"


@dataclass(frozen=True)
class Interaction:
    block: Block
    source: str
    emitted: tuple[str, ...]
    rationale: str
    diagnostics: tuple[tuple[str, int, int], ...] = ()


INTERACTIONS: list[Interaction] = [
    # 1. Sobreposicao completa: as reservadas casam com o padrao-base.
    Interaction(Block.KEYWORD_CORE_X_IDENT_BASE, "int", ("KW_INT",),
              "O lexema inteiro é a palavra reservada, entao reclassifica."),
    Interaction(Block.KEYWORD_CORE_X_IDENT_BASE, "intx", ("IDENT",),
              "Maior lexema vence: IDENT_BASE casa 4 caracteres e KEYWORD_CORE só 3."),
    Interaction(Block.KEYWORD_CORE_X_IDENT_BASE, "print", ("KW_PRINT",),
              "A outra reservada do nucleo, tambem por lexema inteiro."),
    Interaction(Block.KEYWORD_CORE_X_IDENT_BASE, "print2", ("IDENT",),
              "Um digito no fim ja tira a palavra de RCore."),

    # 2. Mesma sobreposicao, agora com as reservadas das extensoes.
    Interaction(Block.KEYWORD_EXT_X_IDENT_BASE, "if", ("KW_IF",),
              "Lexema inteiro pertence a RExt."),
    Interaction(Block.KEYWORD_EXT_X_IDENT_BASE, "ifx", ("IDENT",),
              "Um caractere a mais e a palavra volta a ser identificador."),
    Interaction(Block.KEYWORD_EXT_X_IDENT_BASE, "else2", ("IDENT",),
              "Digito na continuacao afasta de 'else'."),
    Interaction(Block.KEYWORD_EXT_X_IDENT_BASE, "while1", ("IDENT",),
              "Mesma situacao de else2."),

    # 3. Prefixo comum entre atribuicao e igualdade.
    Interaction(Block.ASSIGN_X_REL_OP, "=", ("ASSIGN",),
              "Um so '=' é atribuicao."),
    Interaction(Block.ASSIGN_X_REL_OP, "==", ("EQUAL_EQUAL",),
              "Maior lexema: REL_OP casa dois caracteres, ASSIGN casaria um."),
    Interaction(Block.ASSIGN_X_REL_OP, "===", ("EQUAL_EQUAL", "ASSIGN"),
              "O lexer consome '==' e sobra '=', que vira ASSIGN."),

    # 4. Prefixo comum entre divisao e comentario.
    Interaction(Block.ARITH_OP_X_LINE_COMMENT, "/", ("SLASH",),
              "Uma barra sozinha é divisao."),
    Interaction(Block.ARITH_OP_X_LINE_COMMENT, "//", (),
              "Duas barras iniciam comentario, que é ignorado."),
    Interaction(Block.ARITH_OP_X_LINE_COMMENT, "//x", (),
              "O corpo segue ate a quebra de linha; nada e emitido."),

    # 5. Prefixos dentro da propria familia REL_OP.
    Interaction(Block.REL_OP_PREFIXES, "<", ("LESS",), "Palavra de um caractere da classe."),
    Interaction(Block.REL_OP_PREFIXES, "<=", ("LESS_EQUAL",), "Maior lexema vence sobre '<'."),
    Interaction(Block.REL_OP_PREFIXES, ">", ("GREATER",), "Simetrico de '<'."),
    Interaction(Block.REL_OP_PREFIXES, ">=", ("GREATER_EQUAL",), "Simetrico de '<='."),
    Interaction(Block.REL_OP_PREFIXES, "!", (),
              "'!' esta no alfabeto mas nao casa com classe nenhuma: so existe em '!='.",
              diagnostics=(("!", 1, 1),)),
    Interaction(Block.REL_OP_PREFIXES, "!=", ("BANG_EQUAL",),
              "Com o '=' ao lado, a palavra passa a pertencer a REL_OP."),

    # 6. Operador e literal em sequencia, nunca um lexema so.
    Interaction(Block.ARITH_OP_X_INT_LITERAL, "-10", ("MINUS", "INT_LITERAL"),
              "O sinal nao pertence ao literal (slide 73 - Aula 03)."),
    Interaction(Block.ARITH_OP_X_INT_LITERAL, "+7", ("PLUS", "INT_LITERAL"),
              "Mesma decisao para o '+'."),

    # 7. Delimitadores encostados continuam sendo lexemas separados.
    Interaction(Block.ADJACENT_DELIMITERS, "()", ("LPAREN", "RPAREN"),
              "'()' pertence a L_DelimiterCore², nao a L_DelimiterCore."),
    Interaction(Block.ADJACENT_DELIMITERS, "{}", ("LBRACE", "RBRACE"),
              "Mesma regra para as chaves das extensoes."),
    Interaction(Block.ADJACENT_DELIMITERS, ");", ("RPAREN", "SEMICOLON"),
              "Delimitadores de lexemas diferentes tambem nao se fundem."),

    # 8. Espacos e comentarios sao reconhecidos e nao chegam ao parser.
    Interaction(Block.SKIPPED_CLASSES, "x = 1", ("IDENT", "ASSIGN", "INT_LITERAL"),
              "Os espacos separam os lexemas e somem na saida."),
    Interaction(Block.SKIPPED_CLASSES, "x=1 // fim", ("IDENT", "ASSIGN", "INT_LITERAL"),
              "Comentario no fim da linha nao produz token."),
    Interaction(Block.SKIPPED_CLASSES, "int\tx;", ("KW_INT", "IDENT", "SEMICOLON"),
              "Tabulacao tambem é WHITESPACE e tambem é ignorada."),
]


# Gabaritos do slide, usados como prova de que o catalogo bate com a aula (mesma aula 03)
EXERCISE_10 = Interaction(
    Block.SKIPPED_CLASSES,
    "print(total-2); // ok",
    ("KW_PRINT", "LPAREN", "IDENT", "MINUS", "INT_LITERAL", "RPAREN", "SEMICOLON"),
    "Resultado do slide 82 - Aula 03.",
)

EXERCISE_11 = Interaction(
    Block.ASSIGN_X_REL_OP,
    "intx==10//fim",
    ("IDENT", "EQUAL_EQUAL", "INT_LITERAL"),
    "Resultado do slide 84 - Aula 03, que nomeia o segundo token pela classe REL_OP.",
)