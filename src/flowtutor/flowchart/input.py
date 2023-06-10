

from __future__ import annotations

from flowtutor.flowchart.node import Node
from flowtutor.language import Language


class Input(Node):

    def __init__(self) -> None:
        super().__init__()
        self._shape_points, self.default_color = Language.get_node_shape_data('data')
        self._var_name = ''

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
    def var_name(self) -> str:
        return self._var_name

    @var_name.setter
    def var_name(self, var_name: str) -> None:
        self._var_name = var_name

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return self._shape_points

    @property
    def label(self) -> str:
        if self.var_name:
            return f'{self.var_name} = Input'
        else:
            return self.__class__.__name__

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.var_name) > 0
