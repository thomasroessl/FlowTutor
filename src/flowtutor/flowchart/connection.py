from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.whileloop import WhileLoop

from flowtutor.gui.themes import theme_colors

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'


class Connection:

    def __init__(self, dst_node: Node, src_ind: int, span: bool):
        self._dst_node = dst_node
        self._src_ind = src_ind
        self._span = span

    @property
    def dst_node(self) -> Node:
        return self._dst_node

    @property
    def src_ind(self) -> int:
        return self._src_ind

    @property
    def span(self) -> bool:
        return self._span

    def draw(self, parent: Node) -> None:  # pragma: no cover

        dst_in_points = self.dst_node.in_points
        src_out_points = parent.out_points

        out_x, out_y = src_out_points[int(self.src_ind)]

        text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

        with dpg.draw_node(parent=parent.tag):
            if parent == self.dst_node:
                in_x, in_y = dst_in_points[1]
                offset_y = max(out_y, in_y + 25)
                dpg.draw_line(
                    (out_x + 70, out_y),
                    (out_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_line(
                    (out_x + 70, offset_y),
                    (out_x + 70, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_line(
                    (in_x, offset_y),
                    (out_x + 70, offset_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, offset_y),
                    color=text_color,
                    thickness=2,
                    size=10)
            elif (isinstance(parent, ForLoop) or isinstance(parent, WhileLoop) or isinstance(parent, DoWhileLoop)) and\
                    int(self.src_ind) == 1:
                in_x, in_y = dst_in_points[0]
                dpg.draw_line(
                    (in_x, out_y),
                    (out_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, out_y),
                    color=text_color,
                    thickness=2,
                    size=10)
            elif (isinstance(self.dst_node, ForLoop) or isinstance(self.dst_node, WhileLoop) or
                  isinstance(self.dst_node, DoWhileLoop)) and\
                    self.dst_node.tag in parent.scope:
                in_x, in_y = dst_in_points[1]
                offset_y = max(out_y, in_y) + 25
                dpg.draw_line(
                    (out_x, offset_y),
                    (out_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_line(
                    (in_x, offset_y),
                    (out_x, offset_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, offset_y),
                    color=text_color,
                    thickness=2,
                    size=10)
                pass
            elif isinstance(parent, Conditional) and isinstance(self.dst_node, Connector):
                in_x, in_y = dst_in_points[0]
                dst_offset = 50
                if int(self.src_ind) == 1:
                    in_x += 25
                    line_x = max(out_x, in_x) + dst_offset
                else:
                    in_x -= 25
                    line_x = min(out_x, in_x) - dst_offset
                dpg.draw_line(
                    (out_x, out_y),
                    (line_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_line(
                    (line_x, in_y + 25),
                    (line_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y + 25),
                    (line_x, in_y + 25),
                    color=text_color,
                    thickness=2,
                    size=10)
            elif isinstance(parent, Conditional):
                in_x, in_y = dst_in_points[0]
                dpg.draw_line(
                    (in_x, out_y),
                    (out_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, out_y),
                    color=text_color,
                    thickness=2,
                    size=10)
            elif isinstance(self.dst_node, Connector):
                in_x, in_y = dst_in_points[0]
                dst_offset = 25 if out_x > in_x else -25
                dpg.draw_line(
                    (out_x, in_y + 25),
                    (out_x, out_y),
                    color=text_color,
                    thickness=2)
                dpg.draw_arrow(
                    (in_x + dst_offset, in_y + 25),
                    (out_x, in_y + 25),
                    color=text_color,
                    thickness=2,
                    size=10)
            else:
                dpg.draw_arrow(
                    dst_in_points[0],
                    (out_x, out_y),
                    color=text_color,
                    thickness=2,
                    size=10)
