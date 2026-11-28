"""O contrato entre o compilador e a VM: o artefato vai para JSON e volta igual"""

import pytest

from minilang.bytecode import opcodes
from minilang.bytecode.artifact import FORMAT_VERSION, Artifact, ArtifactError, Instruction


def example_artifact() -> Artifact:
    """O bytecode da seção 3.7 do enunciado: int x; x = 2 + 3 * 4; print(x);"""
    instructions = [
        Instruction(opcodes.PUSH_INT, 0),
        Instruction(opcodes.STORE, 0),
        Instruction(opcodes.PUSH_INT, 3),
        Instruction(opcodes.PUSH_INT, 4),
        Instruction(opcodes.MUL),
        Instruction(opcodes.STORE, 1),
        Instruction(opcodes.PUSH_INT, 2),
        Instruction(opcodes.LOAD, 1),
        Instruction(opcodes.ADD),
        Instruction(opcodes.STORE, 2),
        Instruction(opcodes.LOAD, 2),
        Instruction(opcodes.STORE, 0),
        Instruction(opcodes.LOAD, 0),
        Instruction(opcodes.PRINT),
        Instruction(opcodes.HALT),
    ]
    source_map = [(1, 5), (1, 5), (2, 11), (2, 11), (2, 11), (2, 11), (2, 7), (2, 7), (2, 7), (2, 7),
                  (2, 1), (2, 1), (3, 1), (3, 1), None]
    return Artifact(instructions, ["int", "int", "int"], source_map)


def test_round_trip_keeps_every_field():
    artifact = example_artifact()
    assert Artifact.from_json(artifact.to_json()) == artifact


def test_listing_matches_the_assignment_example():
    lines = example_artifact().listing().split("\n")
    assert lines[:5] == ["PUSH_INT 0", "STORE 0", "PUSH_INT 3", "PUSH_INT 4", "MUL"]
    assert lines[-2:] == ["PRINT", "HALT"]
    assert len(lines) == 15


def test_bool_argument_is_not_confused_with_int():
    artifact = Artifact([Instruction(opcodes.PUSH_BOOL, True), Instruction(opcodes.PUSH_INT, 1)], [], [None, None])
    loaded = Artifact.from_json(artifact.to_json())

    assert loaded.instructions[0].argument is True
    assert type(loaded.instructions[1].argument) is int
    assert loaded.listing() == "PUSH_BOOL true\nPUSH_INT 1"


def test_empty_program_is_only_halt():
    artifact = Artifact([Instruction(opcodes.HALT)], [], [None])
    assert Artifact.from_json(artifact.to_json()) == artifact


def test_every_opcode_is_listed_once():
    assert len(opcodes.ALL) == 20
    assert len(set(opcodes.ALL)) == 20


INVALID = [
    ("isto nao e json", "JSON"),
    ("[]", "objeto"),
    ('{"version": 1, "instructions": []}', "memory_types"),
    ('{"version": 99, "instructions": [], "memory_types": [], "source_map": []}', "versao"),
    ('{"version": 1, "instructions": [{"arg": 1}], "memory_types": [], "source_map": [null]}', "instrucao"),
    ('{"version": 1, "instructions": [], "memory_types": ["float"], "source_map": []}', "tipo"),
    ('{"version": 1, "instructions": [{"op": "HALT"}], "memory_types": [], "source_map": []}', "source_map"),
]


@pytest.mark.parametrize("text, cause", INVALID)
def test_invalid_artifact_is_rejected(text, cause):
    with pytest.raises(ArtifactError) as raised:
        Artifact.from_json(text)
    assert cause in str(raised.value)


def test_unknown_opcode_is_left_for_the_vm():
    """Instrução inválida é diagnóstico de execução, com posição: quem acusa é a VM, não a leitura"""
    text = f'{{"version": {FORMAT_VERSION}, "instructions": [{{"op": "NOPE"}}], "memory_types": [], "source_map": [null]}}'
    assert Artifact.from_json(text).instructions[0].opcode == "NOPE"
