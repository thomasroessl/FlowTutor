from flowtutor.flowchart.node import Node
from flowtutor.language import Language


class FunctionEnd(Node):

    def __init__(self, name: str = ''):
        super().__init__()
        self._shape_points, self.default_color = Language.get_node_shape_data('terminator')
        self._name = name
        self._return_value = '0'

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
        return []

    @property
    def color(self) -> tuple[int, int, int]:
        return self.default_color

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return self._shape_points

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def return_value(self) -> str:
        return self._return_value

    @return_value.setter
    def return_value(self, return_value: str) -> None:
        self._return_value = return_value

    @property
    def label(self) -> str:
        return f'return {self.return_value};'

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.return_value) > 0
