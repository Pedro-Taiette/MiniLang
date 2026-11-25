"""Gramática da MiniLang

dev_note:
    X' é a continuação que sobra ao tirar a recursão à esquerda ou ao fatorar. Os nomes em maiúsculas são os tokens

    Program      -> ItemList
    ItemList     -> Item ItemList | empty
    Item         -> Declaration | Assignment | Output | Block | If | While | For
    Declaration  -> Type IDENT SEMICOLON
    Type         -> KW_INT | KW_BOOL
    Assignment   -> IDENT ASSIGN Expression SEMICOLON
    Output       -> KW_PRINT LPAREN Expression RPAREN SEMICOLON
    Block        -> LBRACE ItemList RBRACE
    If           -> KW_IF LPAREN Expression RPAREN Block Else
    Else         -> KW_ELSE Block | empty
    While        -> KW_WHILE LPAREN Expression RPAREN Block
    For          -> KW_FOR LPAREN Initializer Condition SEMICOLON Increment RPAREN Block
    Initializer  -> Declaration | Assignment | SEMICOLON
    Condition    -> Expression | empty
    Increment    -> IDENT ASSIGN Expression | empty

    Expression   -> Conjunction Expression'
    Expression'  -> KW_OR Conjunction Expression' | empty
    Conjunction  -> Comparison Conjunction'
    Conjunction' -> KW_AND Comparison Conjunction' | empty
    Comparison   -> Addition Comparison'
    Comparison'  -> RelOp Addition | empty
    RelOp        -> EQUAL_EQUAL | BANG_EQUAL | LESS | LESS_EQUAL | GREATER | GREATER_EQUAL
    Addition     -> Term Addition'
    Addition'    -> PLUS Term Addition' | MINUS Term Addition' | empty
    Term         -> Factor Term'
    Term'        -> STAR Factor Term' | SLASH Factor Term' | empty
    Factor       -> LPAREN Expression RPAREN | IDENT | INT_LITERAL | KW_TRUE | KW_FALSE
"""

from .tokens import TokenType

# Os operadores de cada nível de expressão
OR_OPERATORS = [TokenType.KW_OR]
AND_OPERATORS = [TokenType.KW_AND]
EQUALITY_OPERATORS = [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]
ORDERING_OPERATORS = [TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]
COMPARISON_OPERATORS = EQUALITY_OPERATORS + ORDERING_OPERATORS
ADDITIVE_OPERATORS = [TokenType.PLUS, TokenType.MINUS]
MULTIPLICATIVE_OPERATORS = [TokenType.STAR, TokenType.SLASH]
