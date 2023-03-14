from __future__ import annotations


class Language:

    @staticmethod
    def get_data_types() -> list[str]:
        return [
            'char',
            'unsigned char',
            'short',
            'unsigned short',
            'int',
            'unsigned int',
            'long',
            'unsigned long',
            'float',
            'double',
            'long double'
        ]

    @staticmethod
    def get_format_specifiers() -> list[str]:
        return [
            '%c',
            '%c',
            '%hd',
            '%hu',
            '%d',
            '%u',
            '%ld',
            '%lu',
            '%f',
            '%lf',
            '%Lf'
        ]

    @staticmethod
    def get_loop_types() -> list[str]:
        return [
            'while',
            'do while',
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
