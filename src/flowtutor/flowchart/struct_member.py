class StructMember:

    def __init__(self) -> None:
        self._name = ''
        self._type = 'int'
        self._array_size = ''
        self._is_array = False
        self._is_pointer = False

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str):
        self._type = type

    @property
    def is_array(self) -> bool:
        return self._is_array

    @is_array.setter
    def is_array(self, is_array: bool):
        self._is_array = is_array
        if not is_array:
            self.array_size = ''

    @property
    def array_size(self) -> str:
        return self._array_size

    @array_size.setter
    def array_size(self, array_size: str):
        self._array_size = array_size

    @property
    def is_pointer(self) -> bool:
        return self._is_pointer

    @is_pointer.setter
    def is_pointer(self, is_pointer: bool):
        self._is_pointer = is_pointer

    def __repr__(self) -> str:
        return ''.join([
            f'{self.type} ',
            '*' if self.is_pointer else '',
            self.name,
            f'[{self.array_size}]' if self.is_array else '',
            ';'])