from flowtutor.flowchart.node import Node


class FunctionEnd(Node):

    def __init__(self, name: str = ''):
        super().__init__()
        self._name = name
        self._return_value = '0'

    @property
    def shape_width(self):
        return 150

    @property
    def shape_height(self):
        return 75

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return []

    @property
    def color(self):
        return (200, 170, 255)

    @property
    def shape_points(self):
        return [
            (0, 37.5),
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
            (0, 37.5)
        ]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def return_value(self) -> str:
        return self._return_value

    @return_value.setter
    def return_value(self, return_value: str):
        self._return_value = return_value

    @property
    def label(self):
        return f'return {self.return_value};'

    @property
    def is_initialized(self) -> bool:
        return len(self.return_value) > 0
