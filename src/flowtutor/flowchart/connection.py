from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.template import Template

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'


class Connection:
    '''A connection between flochart nodes.'''

    def __init__(self, dst_node: Node, src_ind: int):
        self._dst_node = dst_node
        self._src_ind = src_ind

    def __repr__(self) -> str:
        return f'[{self.src_ind}] -> {self.dst_node}'

    @property
    def dst_node(self) -> Node:
        '''The destination node, that the connection points to.'''
        return self._dst_node

    @property
    def src_ind(self) -> int:
        '''The connection index where the connection originates.'''
        return self._src_ind

    def draw(self, text_color: tuple[int, int, int, int], parent: Node) -> None:  # pragma: no cover
        '''Draws the connection in the dearpygui drawing area.

        Parameters:
            text_color (tuple[int, int, int, int]): The color of the drawn text
            parent (Node): The node where the connection originates.
        '''

        dst_in_points = self.dst_node.in_points
        src_out_points = parent.out_points

        out_x, out_y = src_out_points[int(self.src_ind)]

        with dpg.draw_node(parent=parent.tag):
            if parent == self.dst_node:
                # If the source node and destionation node are the same node, then draw the lines like a loop.
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
            elif (isinstance(parent, Template) and
                  (parent.control_flow == 'loop' or parent.control_flow == 'post-loop')) and\
                    int(self.src_ind) == 1:
                # If the source node is a loop, and the connection goes to the loop body, then draw a horizontal
                # and a vertical line.
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
            elif (isinstance(self.dst_node, Template) and
                  (self.dst_node.control_flow == 'loop' or self.dst_node.control_flow == 'post-loop')) and\
                    self.dst_node.tag in parent.scope:
                # If connection is from a node inside a of a loop body, back to the loop-node, draw lines accordingly.
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
            elif (isinstance(parent, Template) and parent.control_flow == 'decision') and\
                    isinstance(self.dst_node, Connector):
                # If the source node is a decision and the destination is a connector, draw the lines accordingly.
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
            elif isinstance(parent, Template) and parent.control_flow == 'decision':
                # If the source node is a decision and the destination is node in one of its branches.
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
                # If the source node is inside a decision branch and the destination is a connector,
                # draw the lines accordingly.
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
                # In all other cases draw a straight line.
                dpg.draw_arrow(
                    dst_in_points[0],
                    (out_x, out_y),
                    color=text_color,
                    thickness=2,
                    size=10)
