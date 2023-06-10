from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
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
            'data': ([(20.0, 0.0),
                      (150.0, 0.0),
                      (130.0, 75.0),
                      (0.0, 75.0),
                      (20.0, 0.0)],
                     (147, 171, 255)),
            'process': ([(0.0, 0.0),
                         (150, 0),
                         (150, 75),
                         (0, 75),
                         (0, 0)],
                        (255, 255, 170)),
            'preparation': ([(0.0, 37.5),
                             (20, 75),
                             (130, 75),
                             (150, 37.5),
                             (130, 0),
                             (20, 0),
                             (0, 37.5)],
                            (255, 208, 147)),
            'decision': ([(75.0, 0.0),
                          (0, 50),
                          (75, 100),
                          (150, 50),
                          (75, 0)],
                         (255, 170, 170)),
            'terminator': ([(0.0, 37.5),
                            (1, 30),
                            (3, 23),
                            (6, 17),
                            (11, 11),
                            (17, 6),
                            (23, 3),
                            (30, 1),
                            (37.5, 0),
                            (112.5, 0),
                            (120, 1),
                            (127, 3),
                            (133, 6),
                            (139, 11),
                            (144, 17),
                            (147, 23),
                            (149, 30),
                            (150, 37.5),
                            (149, 45),
                            (147, 52),
                            (144, 58),
                            (139, 64),
                            (133, 69),
                            (127, 72),
                            (120, 74),
                            (112.5, 75),
                            (37.5, 75),
                            (30, 74),
                            (23, 72),
                            (17, 69),
                            (11, 64),
                            (6, 58),
                            (3, 52),
                            (1, 45),
                            (0, 37.5)],
                           (200, 170, 255))
        }[node_type]
