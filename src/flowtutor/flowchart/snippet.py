from __future__ import annotations

from flowtutor.flowchart.node import Node
from flowtutor.language import Language


class Snippet(Node):

    def __init__(self) -> None:
        super().__init__()
        self._shape_points, self.default_color = Language.get_node_shape_data('process')
        self._code = ''

    @property
    def shape_width(self) -> int:
        return 150

    @property
    def shape_height(self) -> int:
        return 75

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        return [(75, 0)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        return [(75, 75)]

    @property
    def color(self) -> tuple[int, int, int]:
        return self.default_color if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return self._shape_points

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str) -> None:
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
