
from typing import List

from flowtutor.flowchart.struct_member import StructMember


class StructDefinition:

    def __init__(self) -> None:
        self._name = ''
        self._members: List[StructMember] = [StructMember()]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def members(self) -> List[StructMember]:
        return self._members

    def __repr__(self) -> str:
        members = '\n  '.join([m for m in map(lambda m: str(m), self.members)])
        return f'typedef struct {self.name}_s {{\n  { members }\n}} {self.name}_t;'
