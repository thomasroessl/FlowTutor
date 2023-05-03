from typing import Any, Optional, Tuple
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node, FLOWCHART_TAG
from flowtutor.gui.themes import theme_colors


class ForLoop(Node):

    def __init__(self):
        super().__init__()
        self._var_name = 'i'
        self._start_value = '0'
        self._update = 'i++'
        self._condition = ''

    @property
    def shape_width(self):
        return 150

    @property
    def shape_height(self):
        return 75

    @property
    def raw_in_points(self):
        return [(75, 0), (125, 75)]

    @property
    def raw_out_points(self):
        return [(40, 75), (self.get_right_x(), 37.5)]

    @property
    def color(self):
        return (255, 208, 147) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self):
        return [
            (0, 37.5),
            (20, 75),
            (130, 75),
            (150, 37.5),
            (130, 0),
            (20, 0),
            (0, 37.5)
        ]

    @property
    def label(self):
        if (len(self.condition) > 0 and
            len(self.var_name) > 0 and
            len(self.start_value) > 0 and
                len(self.update) > 0):
            return f'int {self.var_name} = {self.start_value}; {self.condition}; {self.update}'
        else:
            return self.__class__.__name__

    @property
    def condition(self) -> str:
        return self._condition

    @condition.setter
    def condition(self, condition: str):
        self._condition = condition

    @property
    def var_name(self) -> str:
        return self._var_name

    @var_name.setter
    def var_name(self, var_name: str):
        self._var_name = var_name

    @property
    def start_value(self) -> str:
        return self._start_value

    @start_value.setter
    def start_value(self, start_value: str):
        self._start_value = start_value

    @property
    def update(self) -> str:
        return self._update

    @update.setter
    def update(self, update: str):
        self._update = update

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):  # pragma: no cover
        super().draw(mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            return
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

            text_false = 'False'
            text_false_width, _ = dpg.get_text_size(
                text_false)
            dpg.draw_text((pos_x - 10,
                           pos_y + self.shape_height + 5),
                          text_false, color=text_color, size=18)

            text_true = 'True'
            _, text_true_height = dpg.get_text_size(text_true)
            dpg.draw_text((pos_x + 5 + self.get_right_x(),
                           pos_y + self.shape_height/2 - text_true_height - 5),
                          text_true, color=text_color, size=18)

    def delete(self):  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    def has_nested_nodes(self):
        return True

    @property
    def is_initialized(self) -> bool:
        return (len(self.var_name) > 0 and
                len(self.start_value) > 0 and
                len(self.condition) > 0 and
                len(self.update) > 0)

    def get_declaration(self) -> dict[str, Any]:
        return {
            'var_name': self.var_name,
            'var_type': 'int',
            'var_value': 0,
            'array_size': 0,
            'is_array': False,
            'is_pointer':  False,
            'is_static':  False
        }
