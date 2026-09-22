"""Os casos e as interacoes do catalogo (cases.py)"""

from cases import CASES
from interactions import EXERCISE_10, EXERCISE_11, INTERACTIONS

from minilang.analysis.lexer import Lexer
from minilang.spec.lexical_class import Action
from minilang.spec.table import LEXICAL_TABLE
from minilang.spec.tokens import TokenType

CLASSES = {lexical_class.name: lexical_class for lexical_class in LEXICAL_TABLE}


def scan(source: str):
    tokens, diagnostics = Lexer(source).scan_tokens()
    return [t for t in tokens if t.type is not TokenType.EOF], diagnostics


def accepts(name: str, word: str) -> bool:
    if not word:  # nenhuma classe aceita a cadeia vazia
        return False

    tokens, diagnostics = scan(word)
    if diagnostics:
        return False

    lexical_class = CLASSES[name]
    if lexical_class.action is Action.IGNORES:
        return not tokens

    types = set(lexical_class.type_by_lexeme.values()) or {lexical_class.type}
    return len(tokens) == 1 and tokens[0].type in types


def test_todos_os_casos():
    for case in CASES:
        obtained = accepts(case.lexical_class, case.word)
        assert obtained == case.accepted, (
            f"{case.lexical_class} com {case.word!r}: {case.rationale}"
        )


def test_todas_as_interacoes():
    for interaction in [*INTERACTIONS, EXERCISE_10, EXERCISE_11]:
        tokens, diagnostics = scan(interaction.source)

        assert tuple(t.type.value for t in tokens) == interaction.emitted, (
            f"{interaction.source!r}: {interaction.rationale}"
        )
        assert tuple((d.symbol, d.line, d.column) for d in diagnostics) == interaction.diagnostics, (
            f"{interaction.source!r}: {interaction.rationale}"
        )
