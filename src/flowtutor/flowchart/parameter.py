class Parameter:

    def __init__(self) -> None:
        self._name = ''
        self._type = 'int'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str) -> None:
        self._type = type

    def __repr__(self) -> str:
        return f'{self.type} {self.name}'
