from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.node import Node
from flowtutor.language_service import LanguageService


class FunctionEnd(Node):

    @inject
    def __init__(self, name: str = '', language_service: LanguageService = Provide['language_service']):
        super().__init__()
        self._shape_data, self.default_color = language_service.get_node_shape_data('terminator')
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
        return f'return {self.return_value}'

    @property
    def is_initialized(self) -> bool:
        return True
