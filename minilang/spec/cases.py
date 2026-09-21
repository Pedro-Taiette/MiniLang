"""Casos de teste por classe, com as colunas que o slide 96 - aula 03 exige"""

from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    COMMON = "Comum"
    BOUNDARY = "Fronteira"


@dataclass(frozen=True)
class Case:
    lexical_class: str
    word: str
    accepted: bool
    category: Category
    rationale: str


CASES: list[Case] = [
    # KEYWORD_CORE - finita: as duas palavras, mais rejeicoes e fronteiras.
    Case("KEYWORD_CORE", "int", True, Category.BOUNDARY, "Menor palavra da classe e uma das duas únicas."),
    Case("KEYWORD_CORE", "print", True, Category.COMMON, "A outra palavra reservada do núcleo."),
    Case("KEYWORD_CORE", "in", False, Category.BOUNDARY, "Um símbolo a menos que 'int': pertence a L_IdentBase, não aqui."),
    Case("KEYWORD_CORE", "intx", False, Category.BOUNDARY, "Um símbolo a mais: intx ≠ int, então segue IDENT (slide 84 - Aula 03)."),
    Case("KEYWORD_CORE", "Int", False, Category.COMMON, "Maiúsculas e minúsculas são diferentes (slide 67 - Aula 03)."),
    Case("KEYWORD_CORE", "", False, Category.BOUNDARY, "ε não pertence: a grafia tem que ser exata."),

    # IDENT_BASE - infinita.
    Case("IDENT_BASE", "_", True, Category.BOUNDARY, "Menor palavra válida: só o inicial, com continuação vazia."),
    Case("IDENT_BASE", "A1", True, Category.COMMON, "Inicial seguido de um dígito."),
    Case("IDENT_BASE", "total2", True, Category.COMMON, "Letras e dígito na continuação."),
    Case("IDENT_BASE", "resultado", True, Category.COMMON, "Continuação formada só por letras."),
    Case("IDENT_BASE", "intx", True, Category.BOUNDARY, "Um símbolo a mais que 'int' devolve a palavra a esta classe."),
    Case("IDENT_BASE", "", False, Category.BOUNDARY, "O inicial é obrigatório: ε não pertence."),
    Case("IDENT_BASE", "2total", False, Category.BOUNDARY, "Dígito não pode ser o inicial (slide 67 - Aula 03)."),
    Case("IDENT_BASE", "total-2", False, Category.COMMON, "O hífen não está em Continuação; são três lexemas."),
    Case("IDENT_BASE", "á", False, Category.BOUNDARY, "Acento fica fora da MiniLang-Core (slide 67 - Aula 03)."),

    # INT_LITERAL - infinita.
    Case("INT_LITERAL", "0", True, Category.BOUNDARY, "Menor literal válido, com um único dígito."),
    Case("INT_LITERAL", "7", True, Category.COMMON, "Um dígito qualquer."),
    Case("INT_LITERAL", "45", True, Category.COMMON, "Uma ou mais ocorrências de dígito."),
    Case("INT_LITERAL", "007", True, Category.COMMON, "Zeros à esquerda são permitidos (slide 67 - Aula 03)."),
    Case("INT_LITERAL", "1234567890", True, Category.COMMON, "Os dez dígitos, para cobrir todo o conjunto Dígito."),
    Case("INT_LITERAL", "", False, Category.BOUNDARY, "Dígito+ exige ao menos um dígito: ε não pertence."),
    Case("INT_LITERAL", "-10", False, Category.COMMON, "O sinal não pertence ao literal; forma MINUS e INT_LITERAL."),
    Case("INT_LITERAL", "12a", False, Category.BOUNDARY, "Um símbolo a mais, fora de Dígito, e a palavra inteira falha."),
    Case("INT_LITERAL", "1 2", False, Category.COMMON, "O espaço separa dois literais; não é uma palavra só."),
    Case("INT_LITERAL", "a", False, Category.COMMON, "Nenhum dígito: pertence a L_IdentBase, não a esta classe."),

    # ASSIGN - finita: uma unica palavra.
    Case("ASSIGN", "=", True, Category.BOUNDARY, "Única palavra da linguagem, logo também a menor."),
    Case("ASSIGN", "==", False, Category.BOUNDARY, "Um símbolo a mais muda a classe: '==' pertence a L_RelOp."),
    Case("ASSIGN", "", False, Category.BOUNDARY, "ε não pertence."),
    Case("ASSIGN", "=>", False, Category.COMMON, "Os dois símbolos existem, mas a sequência não é palavra da classe."),
    Case("ASSIGN", ":=", False, Category.COMMON, "Atribuição de outras linguagens; ':' nem está no alfabeto-fonte."),

    # ARITH_OP - finita: os quatro operadores.
    Case("ARITH_OP", "+", True, Category.COMMON, "Soma."),
    Case("ARITH_OP", "-", True, Category.COMMON, "Subtração; também aparece antes de literal, mas sempre como lexema próprio."),
    Case("ARITH_OP", "*", True, Category.COMMON, "Multiplicação."),
    Case("ARITH_OP", "/", True, Category.BOUNDARY, "Prefixo de '//': uma barra sozinha é divisão."),
    Case("ARITH_OP", "//", False, Category.BOUNDARY, "Um símbolo a mais inicia comentário (slide 74 - Aula 03)."),
    Case("ARITH_OP", "", False, Category.BOUNDARY, "ε não pertence."),
    Case("ARITH_OP", "+-", False, Category.COMMON, "Dois operadores adjacentes são dois lexemas."),
    Case("ARITH_OP", "%", False, Category.COMMON, "Resto não existe na MiniLang; '%' está fora do alfabeto-fonte."),

    # DELIMITER_CORE - finita: os tres delimitadores.
    Case("DELIMITER_CORE", "(", True, Category.COMMON, "Abertura de parênteses."),
    Case("DELIMITER_CORE", ")", True, Category.COMMON, "Fechamento de parênteses."),
    Case("DELIMITER_CORE", ";", True, Category.COMMON, "Fim de comando."),
    Case("DELIMITER_CORE", "()", False, Category.BOUNDARY, "Um símbolo a mais: '()' pertence a L_DelimiterCore², são dois lexemas."),
    Case("DELIMITER_CORE", ");", False, Category.COMMON, "Delimitadores adjacentes continuam sendo dois lexemas."),
    Case("DELIMITER_CORE", "", False, Category.BOUNDARY, "ε não pertence."),
    Case("DELIMITER_CORE", "{", False, Category.COMMON, "Chave pertence a L_BlockDelimiter, não ao núcleo."),

    # LINE_COMMENT - infinita.
    Case("LINE_COMMENT", "//", True, Category.BOUNDARY, "Menor palavra válida: corpo vazio é permitido."),
    Case("LINE_COMMENT", "//x", True, Category.COMMON, "Um caractere no corpo."),
    Case("LINE_COMMENT", "// comentário", True, Category.COMMON, "Espaços são permitidos no corpo."),
    Case("LINE_COMMENT", "////", True, Category.COMMON, "As duas últimas barras pertencem ao corpo."),
    Case("LINE_COMMENT", "/", False, Category.BOUNDARY, "Um símbolo a menos: uma barra sozinha é ARITH_OP."),
    Case("LINE_COMMENT", "/x", False, Category.COMMON, "Não começa por '//'."),
    Case("LINE_COMMENT", "", False, Category.BOUNDARY, "ε não pertence: o '//' é obrigatório."),
    Case("LINE_COMMENT", "//a\nb", False, Category.BOUNDARY, "A quebra encerra o comentário; '//a' seria lexema separado."),
    Case("LINE_COMMENT", "x//", False, Category.COMMON, "O comentário tem que começar no início do lexema."),

    # WHITESPACE - infinita.
    Case("WHITESPACE", " ", True, Category.BOUNDARY, "Menor palavra válida: uma única ocorrência."),
    Case("WHITESPACE", "\t", True, Category.COMMON, "Tabulação também pertence a B."),
    Case("WHITESPACE", "  ", True, Category.COMMON, "Várias ocorrências do mesmo caractere."),
    Case("WHITESPACE", " \t\n", True, Category.COMMON, "Combinação de espaço, tabulação e nova linha."),
    Case("WHITESPACE", "\r\n", True, Category.COMMON, "CR e NL, a quebra de linha do Windows."),
    Case("WHITESPACE", "", False, Category.BOUNDARY, "B+ exige ao menos um caractere: ε não pertence."),
    Case("WHITESPACE", "a", False, Category.COMMON, "Letra não pertence a B."),
    Case("WHITESPACE", " a", False, Category.BOUNDARY, "Um símbolo fora de B faz a palavra inteira falhar."),
    Case("WHITESPACE", "\v", False, Category.COMMON, "Tabulação vertical não está em B nem no alfabeto-fonte."),

    # KEYWORD_EXT - finita: as tres palavras.
    Case("KEYWORD_EXT", "if", True, Category.BOUNDARY, "Menor palavra da classe, com dois caracteres."),
    Case("KEYWORD_EXT", "else", True, Category.COMMON, "Alternativa do condicional."),
    Case("KEYWORD_EXT", "while", True, Category.COMMON, "Repetição."),
    Case("KEYWORD_EXT", "ifx", False, Category.BOUNDARY, "Um símbolo a mais: 'ifx' segue IDENT (slide 98 - Aula 03)."),
    Case("KEYWORD_EXT", "els", False, Category.BOUNDARY, "Um símbolo a menos que 'else'."),
    Case("KEYWORD_EXT", "IF", False, Category.COMMON, "Maiúsculas e minúsculas são diferentes."),
    Case("KEYWORD_EXT", "", False, Category.BOUNDARY, "ε não pertence."),

    # REL_OP - finita: as seis palavras.
    Case("REL_OP", "==", True, Category.COMMON, "Igualdade, o primeiro dos seis operadores."),
    Case("REL_OP", "!=", True, Category.COMMON, "Diferença, única palavra da classe que começa por '!'."),
    Case("REL_OP", "<=", True, Category.COMMON, "Menor ou igual, de dois caracteres."),
    Case("REL_OP", ">=", True, Category.COMMON, "Maior ou igual, de dois caracteres."),
    Case("REL_OP", "<", True, Category.BOUNDARY, "Menor palavra válida da classe, com um caractere."),
    Case("REL_OP", ">", True, Category.BOUNDARY, "A outra palavra de um caractere só."),
    Case("REL_OP", "!", False, Category.BOUNDARY, "Um símbolo a menos que '!=': '!' sozinho não pertence."),
    Case("REL_OP", "=>", False, Category.COMMON, "Os dois símbolos existem, mas nessa ordem não formam palavra."),
    Case("REL_OP", "=", False, Category.BOUNDARY, "Pertence a L_Assign; um '=' a mais é que faz virar REL_OP."),
    Case("REL_OP", "<==", False, Category.BOUNDARY, "Um símbolo a mais que '<=' sai da linguagem."),
    Case("REL_OP", "", False, Category.BOUNDARY, "ε não pertence a L_RelOp."),

    # BLOCK_DELIMITER - finita: as duas chaves.
    Case("BLOCK_DELIMITER", "{", True, Category.COMMON, "Abertura de bloco."),
    Case("BLOCK_DELIMITER", "}", True, Category.COMMON, "Fechamento de bloco."),
    Case("BLOCK_DELIMITER", "{}", False, Category.BOUNDARY, "Um símbolo a mais: são dois lexemas, não um."),
    Case("BLOCK_DELIMITER", "", False, Category.BOUNDARY, "ε não pertence."),
    Case("BLOCK_DELIMITER", "(", False, Category.COMMON, "Parêntese pertence a L_DelimiterCore, não às extensões."),
]
