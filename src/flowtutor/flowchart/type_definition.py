

class TypeDefinition:
    '''Represents a C style type definition.'''

    def __init__(self) -> None:
        self._name = ''
        self._definition = ''

    @property
    def name(self) -> str:
        '''The name of the type.'''
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def definition(self) -> str:
        '''The definition.'''
        return self._definition

    @definition.setter
    def definition(self, definition: str) -> None:
        self._definition = definition

    def __repr__(self) -> str:
        definition = self.definition.strip()
        return f'typedef {definition}{"" if definition.endswith("*") else " "}{self.name};'
