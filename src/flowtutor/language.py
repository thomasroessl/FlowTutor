from __future__ import annotations
from typing import Optional

from flowtutor.flowchart.flowchart import Flowchart


class Language:

    @staticmethod
    def get_data_types(flowchart: Optional[Flowchart] = None) -> list[str]:

        struct_defintions = list(map(lambda s: f'{s.name}_t', flowchart.struct_definitions)) if flowchart else []
        type_defintions = list(map(lambda s: s.name, flowchart.type_definitions)) if flowchart else []

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
        ] + type_defintions + struct_defintions

    @staticmethod
    def get_standard_headers() -> list[str]:
        return [
            'assert',
            'ctype',
            'errno',
            'error',
            'float',
            'signal',
            'stdio',
            'stdlib',
            'string',
            'math'
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
