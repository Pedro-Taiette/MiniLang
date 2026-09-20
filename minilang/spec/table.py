"""A tabela léxica da MiniLang - as 11 classes do escopo obrigatório

dev_note: 
    A ordem só desempata classes que reclamem a MESMA posição: LINE_COMMENT antes de ARITH_OP por causa de "/", e REL_OP antes de ASSIGN por causa de "=" 
    O maior casamento dentro de uma classe é responsabilidade do consume dela

    As classes de palavra reservada não participam da varredura - elas reclassificam um lexema já reconhecido como IDENT_BASE (slide 72 - Aula 03)
"""

from .lexical_class import Action, LexicalClass
from .recognizers import (
    claims_ident_base,
    claims_int_literal,
    claims_line_comment,
    claims_rel_op,
    claims_symbol,
    claims_whitespace,
    consume_ident_base,
    consume_int_literal,
    consume_line_comment,
    consume_rel_op,
    consume_symbol,
    consume_whitespace,
)
from .tokens import TokenType

LEXICAL_TABLE: list[LexicalClass] = [
    LexicalClass(
        name="LINE_COMMENT",
        finite_language=False,
        purpose="Comentário de linha; reconhecido e ignorado, nunca enviado ao parser. "
                "O corpo vazio é válido e a quebra encerra sem integrar o lexema.",
        description="Começa com duas barras e segue até imediatamente antes da quebra de "
                    "linha. O corpo pode ser vazio e a quebra não integra o lexema.",
        examples=("//", "//x", "// comentário", "////"),
        mathematical_definition='L_LineComment = {"//"w | w ∈ C*}',
        auxiliary_sets=(
            "ΣFonte = caracteres permitidos no arquivo-fonte",
            "CR = retorno de carro, NL = nova linha",
            "C = ΣFonte − {CR, NL}",
        ),
        formal_expression='rComentário = "//" C*',
        action=Action.IGNORES,
        claims=claims_line_comment,
        consume=consume_line_comment,
    ),
    LexicalClass(
        name="WHITESPACE",
        finite_language=False,
        purpose="Separador de lexemas; reconhecido e ignorado, nunca enviado ao parser. "
                "Exige ao menos um caractere: ε ∉ L_Whitespace.",
        description="Uma ou mais ocorrências de espaço, tabulação, retorno de carro ou "
                    "nova linha, em qualquer combinação.",
        examples=(" ", "\t", "  ", " \t\n"),
        mathematical_definition="L_Whitespace = {b_1 b_2 ... b_n | n ≥ 1 e b_i ∈ B}",
        auxiliary_sets=(
            "ESP = espaço, TAB = tabulação, CR = retorno de carro, NL = nova linha",
            "B = {ESP, TAB, CR, NL}",
        ),
        formal_expression="rEspaço = B+ ≡ B B*",
        action=Action.IGNORES,
        claims=claims_whitespace,
        consume=consume_whitespace,
    ),
    LexicalClass(
        name="IDENT_BASE",
        finite_language=False,
        purpose="Padrão-base dos identificadores: produz os candidatos que as "
                "classes de palavra reservada podem reclassificar.",
        description="Uma letra ou um underscore, seguido de zero ou mais letras, "
                    "dígitos ou underscores. Maiúsculas e minúsculas são diferentes.",
        examples=("_", "A1", "total2", "resultado", "intx"),
        mathematical_definition=(
            "L_IdentBase = {c_0 c_1 ... c_n | n ≥ 0, c_0 ∈ Inicial e "
            "c_i ∈ Continuação para 1 ≤ i ≤ n}"
        ),
        auxiliary_sets=(
            "Letra = a ∪ ... ∪ z ∪ A ∪ ... ∪ Z",
            "Dígito = 0 ∪ 1 ∪ ... ∪ 9",
            'Inicial = Letra ∪ "_"',
            'Continuação = Letra ∪ Dígito ∪ "_"',
        ),
        formal_expression="rIdentBase = Inicial Continuação*",
        action=Action.EMITS,
        type=TokenType.IDENT,
        claims=claims_ident_base,
        consume=consume_ident_base,
    ),
    LexicalClass(
        name="INT_LITERAL",
        finite_language=False,
        purpose="Literais inteiros sem sinal: -10 é a sequência MINUS INT_LITERAL, não um literal.",
        description="Uma ou mais ocorrências de dígito. Zeros à esquerda são permitidos, "
                    "e o sinal não faz parte do literal.",
        examples=("0", "7", "45", "007"),
        mathematical_definition="L_IntLiteral = {d_1 d_2 ... d_n | n ≥ 1 e d_i ∈ Dígito}",
        auxiliary_sets=("Dígito = 0 ∪ 1 ∪ ... ∪ 9",),
        formal_expression="rNum = Dígito+ ≡ Dígito Dígito*",
        action=Action.EMITS,
        type=TokenType.INT_LITERAL,
        claims=claims_int_literal,
        consume=consume_int_literal,
    ),
    LexicalClass(
        name="REL_OP",
        finite_language=True,
        purpose="Família dos operadores relacionais; gera EQUAL_EQUAL, BANG_EQUAL, LESS, "
                "LESS_EQUAL, GREATER e GREATER_EQUAL. '!' sozinho não pertence à classe.",
        description="Um dos seis operadores de comparação, de um ou dois caracteres.",
        examples=("==", "!=", "<", "<=", ">", ">="),
        mathematical_definition='L_RelOp = {"==", "!=", "<", "<=", ">", ">="}',
        formal_expression='rRel = "==" ∪ "!=" ∪ "<=" ∪ ">=" ∪ "<" ∪ ">"',
        action=Action.EMITS,
        type_by_lexeme={
            "==": TokenType.EQUAL_EQUAL,
            "!=": TokenType.BANG_EQUAL,
            "<": TokenType.LESS,
            "<=": TokenType.LESS_EQUAL,
            ">": TokenType.GREATER,
            ">=": TokenType.GREATER_EQUAL,
        },
        claims=claims_rel_op,
        consume=consume_rel_op,
    ),
    LexicalClass(
        name="ASSIGN",
        finite_language=True,
        purpose="Operador de atribuição. Um '=' é atribuição; '==' pertence a REL_OP "
                "e casa um lexema mais longo.",
        description="Linguagem finita de uma única palavra, o símbolo de igual sozinho.",
        examples=("=",),
        mathematical_definition='L_Assign = {"="}',
        formal_expression='rAssign = "="',
        action=Action.EMITS,
        type_by_lexeme={"=": TokenType.ASSIGN},
        claims=claims_symbol,
        consume=consume_symbol,
    ),
    LexicalClass(
        name="ARITH_OP",
        finite_language=True,
        purpose="Família dos operadores aritméticos; gera PLUS, MINUS, STAR e SLASH.",
        description="Um dos quatro símbolos de operação aritmética, sempre um único caractere.",
        examples=("+", "-", "*", "/"),
        mathematical_definition='L_ArithOp = {"+", "-", "*", "/"}',
        formal_expression='rArith = "+" ∪ "-" ∪ "*" ∪ "/"',
        action=Action.EMITS,
        type_by_lexeme={
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
        },
        claims=claims_symbol,
        consume=consume_symbol,
    ),
    LexicalClass(
        name="DELIMITER_CORE",
        finite_language=True,
        purpose="Delimitadores do núcleo, que separam e agrupam construções. '()' não "
                "pertence à classe: é uma palavra de L_DelimiterCore².",
        description="Parêntese de abertura, parêntese de fechamento ou ponto e vírgula, "
                    "cada um como um lexema isolado.",
        examples=("(", ")", ";"),
        mathematical_definition='L_DelimiterCore = DCore = {"(", ")", ";"}',
        formal_expression='rDelim = "(" ∪ ")" ∪ ";"',
        action=Action.EMITS,
        type_by_lexeme={
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            ";": TokenType.SEMICOLON,
        },
        claims=claims_symbol,
        consume=consume_symbol,
    ),
    LexicalClass(
        name="BLOCK_DELIMITER",
        finite_language=True,
        purpose="Delimitadores de bloco das extensões. Como DELIMITER_CORE, '{}' são "
                "dois lexemas, não um.",
        description="Chave de abertura ou chave de fechamento, cada uma como um lexema isolado.",
        examples=("{", "}"),
        mathematical_definition='L_BlockDelimiter = DBloco = {"{", "}"}',
        formal_expression='rBloco = "{" ∪ "}"',
        action=Action.EMITS,
        type_by_lexeme={
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
        },
        claims=claims_symbol,
        consume=consume_symbol,
    ),
    LexicalClass(
        name="KEYWORD_CORE",
        finite_language=True,
        purpose="Palavras reservadas do núcleo; reclassificam um lexema de IDENT_BASE. "
                "Linguagem finita contida em L_IdentBase: só o lexema inteiro reclassifica.",
        description="As duas únicas palavras que a MiniLang-Core reserva. Nenhuma outra "
                    "palavra pertence à classe, e a grafia tem que ser exata.",
        examples=("int", "print"),
        mathematical_definition='L_KeywordCore = RCore = {"int", "print"}',
        formal_expression='rKeywordCore = "int" ∪ "print"',
        action=Action.RECLASSIFIES,
        type_by_lexeme={
            "int": TokenType.KW_INT,
            "print": TokenType.KW_PRINT,
        },
    ),
    LexicalClass(
        name="KEYWORD_EXT",
        finite_language=True,
        purpose="Palavras reservadas das extensões; reclassificam um lexema de IDENT_BASE, "
                "na mesma relação de KEYWORD_CORE: ifx continua IDENT.",
        description="As três palavras que as extensões reservam para controle de fluxo.",
        examples=("if", "else", "while"),
        mathematical_definition='L_KeywordExt = RExt = {"if", "else", "while"}',
        formal_expression='rKeywordExt = "if" ∪ "else" ∪ "while"',
        action=Action.RECLASSIFIES,
        type_by_lexeme={
            "if": TokenType.KW_IF,
            "else": TokenType.KW_ELSE,
            "while": TokenType.KW_WHILE,
        },
    ),
]

# As classes que o scan_token percorre, na ordem declarada acima
SCAN_TABLE = [
    lexical_class
    for lexical_class in LEXICAL_TABLE
    if lexical_class.action is not Action.RECLASSIFIES
]

# A tabela que identifier() consulta depois de consumir o identificador inteiro
RESERVED_WORDS: dict[str, TokenType] = {
    lexeme: token_type
    for lexical_class in LEXICAL_TABLE
    if lexical_class.action is Action.RECLASSIFIES
    for lexeme, token_type in lexical_class.type_by_lexeme.items()
}
