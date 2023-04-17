from flowtutor.flowchart.node import Node


class Snippet(Node):

    def __init__(self):
        super().__init__()
        self._code = ''

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
        return [(75, 75)]

    @property
    def color(self):
        return (255, 255, 170) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self):
        return [
            (0, 0),
            (150, 0),
            (150, 75),
            (0, 75),
            (0, 0)
        ]

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        self._code = code

    @property
    def label(self) -> str:
        if self.code:
            return self.code
        else:
            return 'Code Snippet'

    @property
    def is_initialized(self) -> bool:
        return True