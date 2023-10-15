from __future__ import annotations
from typing import TYPE_CHECKING
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.node import Node
from flowtutor.flowchart.parameter import Parameter

if TYPE_CHECKING:
    from flowtutor.language_service import LanguageService


class FunctionStart(Node):

    @inject
    def __init__(self, name: str = '', language_service: LanguageService = Provide['language_service']) -> None:
        super().__init__()
        self._shape_data, self.default_color = language_service.get_node_shape_data('terminator')
        self._name = name
        self._return_type = 'int'
        self._parameters: list[Parameter] = []

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
        return self.default_color

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def return_type(self) -> str:
        return self._return_type

    @return_type.setter
    def return_type(self, return_type: str) -> None:
        self._return_type = return_type

    @property
    def parameters(self) -> list[Parameter]:
        if not hasattr(self, '_parameters'):
            self._parameters = []
        return self._parameters

    @property
    def label(self) -> str:
        return self.name

    @property
    def is_initialized(self) -> bool:
        if hasattr(self, '_parameters'):
            return self.is_comment or all(len(p.name) > 0 for p in self.parameters)
        else:
            return True
