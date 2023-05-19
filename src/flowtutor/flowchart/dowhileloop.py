from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node, FLOWCHART_TAG
from flowtutor.gui.themes import theme_colors

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart


class DoWhileLoop(Node):

    def __init__(self) -> None:
        super().__init__()
        self._condition = ''

    @property
    def shape_width(self) -> int:
        return 150

    @property
    def shape_height(self) -> int:
        return 175

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        return [(75, 0), (125, 175)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        return [(40, 175), (100, 25)]

    @property
    def color(self) -> tuple[int, int, int]:
        return (255, 208, 147) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return [
            (0, 137.5),
            (20, 175),
            (130, 175),
            (150, 137.5),
            (130, 100),
            (20, 100),
            (0, 137.5)
        ]

    @property
    def label(self) -> str:
        if len(self.condition) > 0:
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
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

            text_false = 'False'
            dpg.draw_text((pos_x - 10,
                           pos_y + self.shape_height + 5),
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
