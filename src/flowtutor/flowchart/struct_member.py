class StructMember:
    '''A member of a C style struct.'''

    def __init__(self) -> None:
        self._name = ''
        self._type = 'int'
        self._array_size = ''
        self._is_array = False
        self._is_pointer = False

    @property
    def name(self) -> str:
        '''The name of the struct member.'''
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def type(self) -> str:
        '''The data type of the struct member.'''
        return self._type

    @type.setter
    def type(self, type: str) -> None:
        self._type = type

    @property
    def is_array(self) -> bool:
        '''True if the struct member is an array.'''
        return self._is_array

    @is_array.setter
    def is_array(self, is_array: bool) -> None:
        self._is_array = is_array
        if not is_array:
            self.array_size = ''
        else:
            self.is_pointer = False

    @property
    def array_size(self) -> str:
        '''The size of the array.

        Only applicable for arrays.
        '''
        return self._array_size

    @array_size.setter
    def array_size(self, array_size: str) -> None:
        self._array_size = array_size

    @property
    def is_pointer(self) -> bool:
        '''True if the struct member is a pointer.'''
        return self._is_pointer

    @is_pointer.setter
    def is_pointer(self, is_pointer: bool) -> None:
        self._is_pointer = is_pointer
        if is_pointer:
            self.is_array = False

    def __repr__(self) -> str:
        return ''.join([
            f'{self.type} ',
            '*' if self.is_pointer else '',
            self.name,
            f'[{self.array_size}]' if self.is_array else '',
            ';'])
