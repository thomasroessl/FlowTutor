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
    def get_node_shape_data(node_type: str) -> tuple[list[tuple[float, float]], tuple[int, int, int]]:
        return {
            'io': ([(20.0, 0.0),
                    (150.0, 0.0),
                    (130.0, 75.0),
                    (0.0, 75.0),
                    (20.0, 0.0)],
                   (147, 171, 255))
        }[node_type]
