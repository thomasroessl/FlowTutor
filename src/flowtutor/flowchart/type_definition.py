

class TypeDefinition:

    def __init__(self) -> None:
        self._name = ''
        self._definition = ''

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def definition(self) -> str:
        return self._definition

    @definition.setter
    def definition(self, definition: str) -> None:
        self._definition = definition

    def __repr__(self) -> str:
        definition = self.definition.strip()
        return f'typedef {definition}{"" if definition.endswith("*") else " "}{self.name};'
