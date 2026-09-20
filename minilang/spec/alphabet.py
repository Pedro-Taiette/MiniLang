"""Alfabeto da MiniLang e os conjuntos derivados dele

dev_note: 
    Todos os predicados aceitam a cadeia vazia - é o que `peek()` devolve no fim da entrada - e respondem False para ela
"""

LETTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

DIGITS = frozenset("0123456789")

UNDERSCORE = "_"

IDENT_START = LETTERS | {UNDERSCORE} 
IDENT_CONTINUE = LETTERS | DIGITS | {UNDERSCORE}

CARRIAGE_RETURN = "\r"
NEWLINE = "\n"
LINE_BREAKS = frozenset({CARRIAGE_RETURN, NEWLINE})

# B = {ESP, TAB, CR, NL}
WHITESPACE_CHARS = frozenset({" ", "\t"}) | LINE_BREAKS

SYMBOLS = frozenset("+-*/=();") | frozenset("<>!{}")

SOURCE_ALPHABET = LETTERS | DIGITS | {UNDERSCORE} | WHITESPACE_CHARS | SYMBOLS


def is_letter(symbol: str) -> bool:
    return symbol in LETTERS


def is_digit(symbol: str) -> bool:
    return symbol in DIGITS


def is_ident_start(symbol: str) -> bool:
    return symbol in IDENT_START


def is_ident_continue(symbol: str) -> bool:
    return symbol in IDENT_CONTINUE


def is_whitespace(symbol: str) -> bool:
    return symbol in WHITESPACE_CHARS


def is_line_break(symbol: str) -> bool:
    return symbol in LINE_BREAKS


def is_source_symbol(symbol: str) -> bool:
    return symbol in SOURCE_ALPHABET
