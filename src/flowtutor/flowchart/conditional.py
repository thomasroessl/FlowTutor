

from typing import Optional, Tuple
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node, FLOWCHART_TAG
from flowtutor.gui.themes import theme_colors


class Conditional(Node):

    def __init__(self):
        super().__init__()
        self._condition = ''

    @property
    def shape_width(self):
        return 150

    @property
    def shape_height(self):
        return 100

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return [(self.get_left_x(), 50),
                (self.get_right_x(), 50)]

    @property
    def color(self):
        return (255, 170, 170) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self):
        return [
            (75, 0),
            (0, 50),
            (75, 100),
            (150, 50),
            (75, 0)
        ]

    @property
    def label(self):
        if self.condition:
            return self.condition
        else:
            return self.__class__.__name__

    @property
    def condition(self) -> str:
        return self._condition

    @condition.setter
    def condition(self, condition: str):
        self._condition = condition

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):  # pragma: no cover
        super().draw(mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            return
        # Draw labels for the branches
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

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

    def delete(self):  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    def has_nested_nodes(self):
        return True

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.condition) > 0
