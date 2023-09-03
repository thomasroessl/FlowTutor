from __future__ import annotations
from ast import literal_eval
from typing import TYPE_CHECKING, Any, Optional
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.language import Language
from flowtutor.flowchart.node import Node
from flowtutor.gui.themes import theme_colors

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart
    from flowtutor.language_service import LanguageService


class Template(Node):

    @inject
    def __init__(self, data: Any, language_service: LanguageService = Provide['language_service']) -> None:
        super().__init__()
        self.language_service = language_service
        self._data = data
        self._control_flow: Optional[str] = data['control_flow'] if 'control_flow' in data else None
        self._body: Optional[str] = data['body'] if 'body' in data else None
        self._shape_data, default_color = Language.get_node_shape_data(data['shape_id'])
        if self.control_flow == 'post-loop':
            self.shape_data[0] = list(map(lambda p: (p[0], p[1] + 100), self.shape_data[0]))
        self._shape_points = self.shape_data[0]

        self._shape_height = max(map(lambda p: p[1], self.shape_points)) - min(map(lambda p: p[1], self.shape_points))

        self._color: tuple[int, int, int] = literal_eval(data['color']) if 'color' in data else default_color
        self._values: dict[str, str] = {}
        if 'parameters' in data:
            self._parameters: list[Any] = data['parameters']
            for parameter in self.parameters:
                if 'default' in parameter:
                    self.values[parameter['name']] = parameter['default']
                else:
                    self.values[parameter['name']] = ''

    def __repr__(self) -> str:
        return f'({self.data["label"]}: {self.__class__.__name__})'

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
    def body(self) -> Optional[str]:
        return self._body

    @property
    def control_flow(self) -> Optional[str]:
        return self._control_flow

    @property
    def shape_width(self) -> int:
        return 150

    @property
    def shape_height(self) -> int:
        return int(self._shape_height)

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        if self.control_flow == 'loop':
            return [(75, 0), (125, 75)]
        elif self.control_flow == 'post-loop':
            return [(75, 0), (125, 175)]
        else:
            return [(75, 0)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        if self.control_flow == 'decision':
            return [(self.get_left_x(), 50), (self.get_right_x(), 50)]
        elif self.control_flow == 'loop':
            return [(40, 75), (self.get_right_x(), self.shape_height / 2)]
        elif self.control_flow == 'post-loop':
            return [(40, 175), (100, 25)]
        else:
            return [(75, 75)]

    def draw(self,
             flowchart: Flowchart,
             is_selected: bool = False) -> None:  # pragma: no cover
        super().draw(flowchart, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            return
        with dpg.draw_node(
                tag=tag,
                parent=self.tag):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

            if self.control_flow == 'post-loop':
                text_false = 'False'
                dpg.draw_text((pos_x - 10,
                               pos_y + self.shape_height + 105),
                              text_false, color=text_color, size=18)
                text_true = 'True'
                _, text_true_height = dpg.get_text_size(text_true)
                dpg.draw_text((pos_x + 80,
                               pos_y + 100 - text_true_height - 5),
                              text_true, color=text_color, size=18)
                dpg.draw_arrow(
                    (pos_x + 75, pos_y + 50),
                    (pos_x + 75, pos_y + 100),
                    color=text_color,
                    thickness=2,
                    size=10)
            elif self.control_flow == 'decision':
                text_false = 'False'
                text_false_width, text_false_height = dpg.get_text_size(
                    text_false)
                dpg.draw_text((pos_x - text_false_width - 5 + self.get_left_x(),
                               pos_y + self.shape_height/2 - text_false_height - 5),
                              text_false, color=text_color, size=18)

                text_true = 'True'
                _, text_true_height = dpg.get_text_size(text_true)
                dpg.draw_text((pos_x + 5 + self.get_right_x(),
                               pos_y + self.shape_height/2 - text_true_height - 5),
                              text_true, color=text_color, size=18)
            elif self.control_flow == 'loop':
                text_false = 'False'
                dpg.draw_text((pos_x - 10,
                               pos_y + self.shape_height + 5),
                              text_false, color=text_color, size=18)

                text_true = 'True'
                _, text_true_height = dpg.get_text_size(text_true)
                dpg.draw_text((pos_x + 5 + self.get_right_x(),
                               pos_y + self.shape_height/2 - text_true_height - 5),
                              text_true, color=text_color, size=18)

    @property
    def color(self) -> tuple[int, int, int]:
        return self._color if self.is_initialized else (255, 0, 0)

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str) -> None:
        self._code = code

    @property
    def label(self) -> str:
        if 'node_label' in self.data:
            return self.language_service.render_line(str(self.data['node_label']), self.values)
        else:
            return str(self.data['label'])

    @property
    def is_initialized(self) -> bool:
        return True
