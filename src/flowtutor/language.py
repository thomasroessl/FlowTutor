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
    def get_loop_types() -> list[str]:
        return [
            'while',
            'for'
        ]

    @staticmethod
    def has_var_declaration() -> bool:
        return True

    @staticmethod
    def has_pointers() -> bool:
        return True

    @staticmethod
    def has_arrays() -> bool:
        return True

    @staticmethod
    def has_for_loops() -> bool:
        return True
