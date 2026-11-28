"""Instruções da máquina virtual (seção F do enunciado)

O compilador gera estes nomes e a VM os executa. Ficam como texto porque é assim que vão para o artefato.
"""

# Pilha e memória
PUSH_INT = "PUSH_INT"       # argumento: a constante inteira
PUSH_BOOL = "PUSH_BOOL"     # argumento: true ou false
LOAD = "LOAD"               # argumento: a posição de memória
STORE = "STORE"             # argumento: a posição de memória

# Aritméticas: int x int -> int
ADD = "ADD"
SUB = "SUB"
MUL = "MUL"
DIV = "DIV"

# Relacionais: int x int -> bool
LT = "LT"
LE = "LE"
GT = "GT"
GE = "GE"

# Igualdade: operandos do mesmo tipo -> bool
EQ = "EQ"
NE = "NE"

# Lógicas: bool x bool -> bool
AND = "AND"
OR = "OR"

# Controle e saída
JMP = "JMP"                 # argumento: o índice da instrução de destino
JMP_FALSE = "JMP_FALSE"     # argumento: o índice da instrução de destino
PRINT = "PRINT"
HALT = "HALT"

ARITHMETIC = [ADD, SUB, MUL, DIV]
ORDERING = [LT, LE, GT, GE]
EQUALITY = [EQ, NE]
LOGICAL = [AND, OR]
BINARY = ARITHMETIC + ORDERING + EQUALITY + LOGICAL

JUMPS = [JMP, JMP_FALSE]
WITH_ARGUMENT = [PUSH_INT, PUSH_BOOL, LOAD, STORE] + JUMPS

ALL = WITH_ARGUMENT + BINARY + [PRINT, HALT]
