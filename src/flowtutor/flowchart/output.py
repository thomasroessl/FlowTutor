from __future__ import annotations

from flowtutor.flowchart.node import Node
from flowtutor.language import Language


class Output(Node):

    def __init__(self) -> None:
        super().__init__()
        self._shape_points, self.default_color = Language.get_node_shape_data('data')
        self._format_string = ''
        self._arguments = ''

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
    def arguments(self) -> str:
        return self._arguments

    @arguments.setter
    def arguments(self, arguments: str) -> None:
        self._arguments = arguments

    @property
    def format_string(self) -> str:
        return self._format_string

    @format_string.setter
    def format_string(self, format_string: str) -> None:
        self._format_string = format_string

    @property
    def label(self) -> str:
        if self.format_string and self.arguments:
            return f'Output:\n{self.format_string}: {self.arguments}'
        elif self.format_string:
            return f'Output:\n{self.format_string}'
        else:
            return self.__class__.__name__

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.format_string) > 0
