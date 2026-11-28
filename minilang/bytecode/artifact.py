"""Artefato de bytecode: o que o compilador grava e a VM lê

Formato (JSON):
    {
      "version": 1,
      "instructions": [{"op": "PUSH_INT", "arg": 2}, {"op": "ADD"}, ...],
      "memory_types": ["int", "bool", ...],
      "source_map": [[linha, coluna], null, ...]
    }

memory_types tem uma entrada por posição de memória. source_map tem uma entrada por instrução.
"""

import json
from dataclasses import dataclass, field

FORMAT_VERSION = 1

MEMORY_TYPES = ["int", "bool"]


class ArtifactError(Exception):
    """O texto lido não é um artefato deste formato"""


@dataclass
class Instruction:
    opcode: str
    argument: object = None     # int, bool ou None, conforme o opcode

    def __str__(self) -> str:
        if self.argument is None:
            return self.opcode
        if self.argument is True:
            return f"{self.opcode} true"
        if self.argument is False:
            return f"{self.opcode} false"
        return f"{self.opcode} {self.argument}"


@dataclass
class Artifact:
    instructions: list = field(default_factory=list)
    memory_types: list = field(default_factory=list)
    source_map: list = field(default_factory=list)      # (linha, coluna) ou None
    version: int = FORMAT_VERSION

    def listing(self) -> str:
        return "\n".join(str(instruction) for instruction in self.instructions)

    def to_json(self) -> str:
        instructions = []
        for instruction in self.instructions:
            record = {"op": instruction.opcode}
            if instruction.argument is not None:
                record["arg"] = instruction.argument
            instructions.append(record)

        source_map = []
        for position in self.source_map:
            if position is None:
                source_map.append(None)
            else:
                source_map.append([position[0], position[1]])

        return json.dumps({
            "version": self.version,
            "instructions": instructions,
            "memory_types": self.memory_types,
            "source_map": source_map,
        }, indent=2)

    @staticmethod
    def from_json(text: str) -> "Artifact":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ArtifactError(f"artefato nao e um JSON valido: {error.msg}")

        if not isinstance(data, dict):
            raise ArtifactError("artefato deve ser um objeto JSON")

        for name in ["version", "instructions", "memory_types", "source_map"]:
            if name not in data:
                raise ArtifactError(f"artefato sem o campo '{name}'")

        if data["version"] != FORMAT_VERSION:
            raise ArtifactError(f"versao {data['version']!r} nao suportada (esperada {FORMAT_VERSION})")

        instructions = []
        for record in data["instructions"]:
            if not isinstance(record, dict) or not isinstance(record.get("op"), str):
                raise ArtifactError(f"instrucao mal formada: {record!r}")
            instructions.append(Instruction(record["op"], record.get("arg")))

        for memory_type in data["memory_types"]:
            if memory_type not in MEMORY_TYPES:
                raise ArtifactError(f"tipo de memoria desconhecido: {memory_type!r}")

        if len(data["source_map"]) != len(instructions):
            raise ArtifactError("source_map deve ter uma entrada por instrucao")

        source_map = []
        for position in data["source_map"]:
            if position is None:
                source_map.append(None)
            else:
                source_map.append((position[0], position[1]))

        return Artifact(instructions, data["memory_types"], source_map, data["version"])
