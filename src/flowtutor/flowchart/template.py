from __future__ import annotations
from ast import literal_eval
from typing import Any
from flowtutor.flowchart.node import Node

from flowtutor.language import Language


class Template(Node):

    def __init__(self, data: Any) -> None:
        super().__init__()
        self._data = data
        self._shape_points, default_color = Language.get_node_shape_data(data['shape_id'])
        self._color: tuple[int, int, int] = literal_eval(data['color']) if 'color' in data else default_color
        self._values: dict[str, str] = {}
        if 'parameters' in data:
            self._parameters: list[Any] = data['parameters']
            for parameter in self.parameters:
                if 'default' in parameter:
                    self.values[parameter['name']] = parameter['default']
                else:
                    self.values[parameter['name']] = ''

    @property
    def data(self) -> Any:
        return self._data

    @property
    def parameters(self) -> list[Any]:
        return self._parameters

    @property
    def values(self) -> dict[str, str]:
        return self._values

    @property
    def body(self) -> str:
        body = self.data['body']
        result = ''
        if isinstance(body, list):
            result = '\n'.join(body)
        else:
            result = str(body)

        for k, v in self.values.items():
            result = result.replace(f'${{{k}}}', v)

        return result

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
        return self._color if self.is_initialized else (255, 0, 0)

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
        return str(self.data['label'])

    @property
    def is_initialized(self) -> bool:
        return True
