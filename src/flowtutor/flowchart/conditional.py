from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node, FLOWCHART_TAG
from flowtutor.gui.themes import theme_colors
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart


class Conditional(Node):

    def __init__(self) -> None:
        super().__init__()
        self._shape_points, self.default_color = Language.get_node_shape_data('decision')
        self._condition = ''

    @property
    def shape_width(self) -> int:
        return 150

    @property
    def shape_height(self) -> int:
        return 100

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        return [(75, 0)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        return [(self.get_left_x(), 50),
                (self.get_right_x(), 50)]

    @property
    def color(self) -> tuple[int, int, int]:
        return self.default_color if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return self._shape_points

    @property
    def label(self) -> str:
        if self.condition:
            return self.condition
        else:
            return self.__class__.__name__

    @property
    def condition(self) -> str:
        return self._condition

    @condition.setter
    def condition(self, condition: str) -> None:
        self._condition = condition

    def draw(self,
             flowchart: Flowchart,
             mouse_pos: Optional[tuple[int, int]],
             is_selected: bool = False) -> None:  # pragma: no cover
        super().draw(flowchart, mouse_pos, is_selected)
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

    def delete(self) -> None:  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    def has_nested_nodes(self) -> bool:
        return True

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.condition) > 0
