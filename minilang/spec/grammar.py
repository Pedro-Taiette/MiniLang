"""Catálogo da gramática da MiniLang (G2 expandida com blocos e controle de fluxo) para o analisador sintático

    Cada não-terminal carrega a definição teórica dos slides (produções de G2, FIRST e FOLLOW) e aponta para o
    método do Parser que o implementa. Os conjuntos são só notação: o parser é descendente recursivo escrito à
    mão e não é dirigido por esta tabela

    A tabela é a fonte única dos operadores de cada nível (ADDITIVE_OPERATORS e MULTIPLICATIVE_OPERATORS) e o
    lugar onde a correspondência de nomes vira dado verificável: o nome do slide (Expr), o da função do
    enunciado (expressao) e o do método do Parser (expression) ficam lado a lado

    As extensões de fluxo (ComandoIf, ComandoWhile, ComandoFor) usam [X] para parte opcional, como no README: o
    parser decide se ela está presente olhando um único token, e test_grammar confere que essa decisão é LL(1)
"""

from dataclasses import dataclass

from .tokens import TokenType

# Conjuntos que se repetem entre as entradas
_COMMAND_START = frozenset({TokenType.KW_INT, TokenType.IDENT, TokenType.KW_PRINT,
                            TokenType.KW_IF, TokenType.KW_WHILE, TokenType.KW_FOR})
_COMMAND_FOLLOW = _COMMAND_START | {TokenType.EOF, TokenType.RBRACE}
_EXPRESSION_START = frozenset({TokenType.LPAREN, TokenType.IDENT, TokenType.INT_LITERAL})
_RELATIONAL_OPERATORS = frozenset({TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS,
                                   TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL})
_CONDITION_END = frozenset({TokenType.SEMICOLON, TokenType.RPAREN})
_EXPRESSION_END = _CONDITION_END | _RELATIONAL_OPERATORS
# Declaracao e Atribuicao também abrem o for: depois delas vem a condição ou o ';' de condição vazia
_INITIALIZER_FOLLOW = _COMMAND_FOLLOW | _EXPRESSION_START | {TokenType.SEMICOLON}


@dataclass(frozen=True)
class Production:
    name: str                       # Não-terminal dos slides (A06/A07): "Expr"
    function: str                   # Função que o enunciado pede (T02 s5): "expressao"
    method: str                     # Método do Parser que a implementa: "expression"
    purpose: str
    rules: tuple[str, ...]          # Produções de G2, incluindo a continuação - só documentação
    first: frozenset[TokenType]     # Sem ε; `nullable` diz se ε entra
    follow: frozenset[TokenType]
    examples: tuple[str, ...]
    nullable: bool = False
    operators: frozenset[TokenType] = frozenset()   # Só Expr, Termo e Condicao


GRAMMAR: list[Production] = [
    Production(
        name="Programa",
        function="programa",
        method="program",
        purpose="Símbolo inicial: uma lista de itens seguida do fim da entrada. O programa vazio é válido.",
        rules=("Programa → ListaItens",),
        first=_COMMAND_START,
        follow=frozenset({TokenType.EOF}),
        nullable=True,
        examples=("", "print(y);", "int x;\nx = 2 + 3 * 4;\nprint(x);"),
    ),
    Production(
        name="ListaItens",
        function="lista_itens",
        method="item_list",
        purpose=("Zero ou mais comandos em sequência. Termina no EOF ou, dentro de um Bloco, no '}'; qualquer "
                 "outro token tem que iniciar um item."),
        rules=("ListaItens → Item ListaItens | ε",),
        first=_COMMAND_START,
        follow=frozenset({TokenType.EOF, TokenType.RBRACE}),
        nullable=True,
        examples=("", "int x;", "int x;\nx = 1;\nprint(x);"),
    ),
    Production(
        name="Item",
        function="item",
        method="item",
        purpose="Um comando. O primeiro token decide qual: 'int', identificador, 'print', 'if', 'while' ou 'for'.",
        rules=("Item → Declaracao | Atribuicao | Saida | ComandoIf | ComandoWhile | ComandoFor",),
        first=_COMMAND_START,
        follow=_COMMAND_FOLLOW,
        examples=("int x;", "x = 10;", "print(x);"),
    ),
    Production(
        name="Declaracao",
        function="declaracao",
        method="declaration",
        purpose="Declara uma variável inteira. Não há declaração com inicialização (A06 s89).",
        rules=("Declaracao → KW_INT IDENT SEMICOLON",),
        first=frozenset({TokenType.KW_INT}),
        follow=_INITIALIZER_FOLLOW,
        examples=("int x;", "int total;", "int intx;"),
    ),
    Production(
        name="Atribuicao",
        function="atribuicao",
        method="assignment",
        purpose="Atribui o valor de uma expressão a uma variável.",
        rules=("Atribuicao → IDENT ASSIGN Expr SEMICOLON",),
        first=frozenset({TokenType.IDENT}),
        follow=_INITIALIZER_FOLLOW,
        examples=("x = 10;", "x = 2 + 3 * 4;", "total = saldo + 10 - desconto;"),
    ),
    Production(
        name="Saida",
        function="saida",
        method="output",
        purpose="Imprime o valor de uma expressão entre parênteses.",
        rules=("Saida → KW_PRINT LPAREN Expr RPAREN SEMICOLON",),
        first=frozenset({TokenType.KW_PRINT}),
        follow=_COMMAND_FOLLOW,
        examples=("print(y);", "print(2 + 3 * 4);", "print((2 + 3) * 4);"),
    ),
    Production(
        name="Expr",
        function="expressao",
        method="expression",
        purpose="Nível de menor precedência: soma e subtração, associativas à esquerda na AST.",
        rules=(
            "Expr → Termo Expr′",
            "Expr′ → PLUS Termo Expr′ | MINUS Termo Expr′ | ε",
        ),
        first=_EXPRESSION_START,
        follow=_EXPRESSION_END,
        operators=frozenset({TokenType.PLUS, TokenType.MINUS}),
        examples=("2", "total-2", "10 - 3 - 2", "saldo + 10 - desconto", "(2 + 3) * 4"),
    ),
    Production(
        name="Termo",
        function="termo",
        method="term",
        purpose="Nível intermediário: multiplicação e divisão, associativas à esquerda na AST.",
        rules=(
            "Termo → Fator Termo′",
            "Termo′ → STAR Fator Termo′ | SLASH Fator Termo′ | ε",
        ),
        first=_EXPRESSION_START,
        follow=frozenset({TokenType.PLUS, TokenType.MINUS}) | _EXPRESSION_END,
        operators=frozenset({TokenType.STAR, TokenType.SLASH}),
        examples=("2", "2 * 3", "8 / 4 / 2", "a * (b - c) / d"),
    ),
    Production(
        name="Fator",
        function="fator",
        method="factor",
        purpose="Nível de maior precedência: literal, identificador ou expressão entre parênteses.",
        rules=("Fator → LPAREN Expr RPAREN | IDENT | INT_LITERAL",),
        first=_EXPRESSION_START,
        follow=frozenset({TokenType.STAR, TokenType.SLASH, TokenType.PLUS, TokenType.MINUS}) | _EXPRESSION_END,
        examples=("x", "007", "(2 + 3)", "((x))"),
    ),
    Production(
        name="Bloco",
        function="bloco",
        method="block",
        purpose="Comandos entre chaves. Reaproveita ListaItens, mas o laço de block() para no '}' em vez do EOF.",
        rules=("Bloco → LBRACE ListaItens RBRACE",),
        first=frozenset({TokenType.LBRACE}),
        follow=_COMMAND_FOLLOW | {TokenType.KW_ELSE},
        examples=("{ }", "{ print(x); }", "{ int x; x = 1; }"),
    ),
    Production(
        name="Condicao",
        function="condicao",
        method="condition",
        purpose=("Expressão com no máximo um operador relacional: não é associativa, então 'a < b < c' é erro. "
                 "Só aparece em if, while e for."),
        rules=(
            "Condicao → Expr [ OpRelacional Expr ]",
            "OpRelacional → EQUAL_EQUAL | BANG_EQUAL | LESS | LESS_EQUAL | GREATER | GREATER_EQUAL",
        ),
        first=_EXPRESSION_START,
        follow=_CONDITION_END,
        operators=_RELATIONAL_OPERATORS,
        examples=("x", "a == b", "a != b", "i < 10", "i <= 10", "x > 0", "x + 1 >= y * 2"),
    ),
    Production(
        name="ComandoIf",
        function="comando_if",
        method="if_statement",
        purpose="Desvio condicional com 'else' opcional. As chaves são obrigatórias, então não há else pendente.",
        rules=("ComandoIf → KW_IF LPAREN Condicao RPAREN Bloco [ KW_ELSE Bloco ]",),
        first=frozenset({TokenType.KW_IF}),
        follow=_COMMAND_FOLLOW,
        examples=("if (x) { }", "if (x > 0) { print(x); }", "if (a == b) { x = 1; } else { x = 2; }"),
    ),
    Production(
        name="ComandoWhile",
        function="comando_while",
        method="while_statement",
        purpose="Laço com a condição testada antes de cada volta.",
        rules=("ComandoWhile → KW_WHILE LPAREN Condicao RPAREN Bloco",),
        first=frozenset({TokenType.KW_WHILE}),
        follow=_COMMAND_FOLLOW,
        examples=("while (x) { }", "while (i < 10) { i = i + 1; }"),
    ),
    Production(
        name="ComandoFor",
        function="comando_for",
        method="for_statement",
        purpose=("Laço com inicialização, condição e incremento. A inicialização já traz o próprio ';' (ou é só "
                 "o ';'); condição e incremento são opcionais."),
        rules=(
            "ComandoFor → KW_FOR LPAREN Inicializacao [ Condicao ] SEMICOLON [ Incremento ] RPAREN Bloco",
            "Inicializacao → Declaracao | Atribuicao | SEMICOLON",
        ),
        first=frozenset({TokenType.KW_FOR}),
        follow=_COMMAND_FOLLOW,
        examples=(
            "for (;;) { }",
            "for (int i; i < 3; i = i + 1) { print(i); }",
            "for (i = 0; i < n; i = i + 1) { x = x + i; }",
        ),
    ),
    Production(
        name="Incremento",
        function="incremento",
        method="increment",
        purpose="Atribuição sem o ';' final: no for, quem fecha o incremento é o ')'.",
        rules=("Incremento → IDENT ASSIGN Expr",),
        first=frozenset({TokenType.IDENT}),
        follow=frozenset({TokenType.RPAREN}),
        examples=("i = i + 1", "x = 0"),
    ),
]

PRODUCTIONS = {production.name: production for production in GRAMMAR}

# Os conjuntos que o Parser consulta - derivados da tabela, nunca repetidos 
ADDITIVE_OPERATORS = PRODUCTIONS["Expr"].operators
MULTIPLICATIVE_OPERATORS = PRODUCTIONS["Termo"].operators