from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import FLOWCHART_TAG, Node
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart


class Call(Node):

    def __init__(self) -> None:
        super().__init__()
        self._shape_points, _ = Language.get_node_shape_data('process')
        self._expression = ''

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
        return (200, 170, 255) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return self._shape_points

    @property
    def label(self) -> str:
        if self.expression:
            return self.expression
        else:
            return self.__class__.__name__

    @property
    def expression(self) -> str:
        return self._expression

    @expression.setter
    def expression(self, expression: str) -> None:
        self._expression = expression

    def draw(self,
             flowchart: Flowchart,
             mouse_pos: Optional[tuple[int, int]],
             is_selected: bool = False) -> None:  # pragma: no cover
        super().draw(flowchart, mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            return
        # Draw extra lines for the declaration node
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = (0, 0, 0)

            dpg.draw_line(
                (pos_x + 10 + self.get_left_x(), pos_y),
                (pos_x + 10 + self.get_left_x(), pos_y + self.shape_height),
                color=text_color,
                thickness=1)
            dpg.draw_line(
                (pos_x - 10 + self.get_right_x(), pos_y),
                (pos_x - 10 + self.get_right_x(), pos_y + self.shape_height),
                color=text_color,
                thickness=1)

    def delete(self) -> None:  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    @property
    def is_initialized(self) -> bool:
        return self.is_comment or len(self.expression) > 0
