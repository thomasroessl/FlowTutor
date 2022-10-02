class Language:

    @staticmethod
    def get_data_types() -> list[str]:
        return [
            'char',
            'short',
            'int',
            'long',
            'float',
            'double'
        ]

    @staticmethod
    def has_pointers() -> bool:
        return True

    @staticmethod
    def has_arrays() -> bool:
        return True
