import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.loop import Loop


class Connection:

    def __init__(self, src: str, src_ind: int, dst: str, dst_ind: int = 0):
        self._src = src
        self._src_ind = src_ind
        self._dst = dst
        self._dst_ind = dst_ind

    @property
    def tag(self) -> str:
        return f"{self.src}[{self.src_ind}]->{self.dst}[{self.dst_ind}]"

    @property
    def src(self) -> str:
        return self._src

    @property
    def src_ind(self) -> int:
        return self._src_ind

    @property
    def dst_ind(self) -> int:
        return self._dst_ind

    @property
    def dst(self) -> str:
        return self._dst

    def find_node(self, tag: str, nodes: list[Node]):
        return next(filter(lambda n: n.tag == tag, nodes), None)

    def draw(self, parent: str, nodes: list[Node]):

        src_node = self.find_node(self.src, nodes)
        dst_node = self.find_node(self.dst, nodes)

        if src_node is None or dst_node is None:
            return

        dst_in_points = dst_node.in_points
        src_out_points = src_node.out_points

        out_x, out_y = src_out_points[int(self.src_ind)]

        dst_ind = 0 if len(dst_in_points) == 1 else int(self.dst_ind)

        with dpg.draw_node(
                tag=self.tag,
                parent=parent):
            if src_node == dst_node:
                in_x, in_y = dst_in_points[1]
                dpg.draw_line(
                    (out_x + 60, out_y),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_line(
                    (out_x + 60, out_y + 75),
                    (out_x + 60, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_line(
                    (out_x - 40, out_y + 75),
                    (out_x + 60, out_y + 75),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (out_x - 40, out_y + 75),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            elif isinstance(src_node, Loop) and int(self.src_ind) == 1:
                in_x, in_y = dst_in_points[dst_ind]
                dpg.draw_line(
                    (in_x, out_y),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, out_y),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            elif isinstance(dst_node, Loop) and int(self.dst_ind) == 1:
                in_x, in_y = dst_in_points[dst_ind]
                dpg.draw_line(
                    (out_x, out_y + 50),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_line(
                    (in_x, out_y + 50),
                    (out_x, out_y + 50),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, out_y + 50),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            elif isinstance(src_node, Conditional) and isinstance(dst_node, Connector):
                in_x, in_y = dst_in_points[dst_ind]
                dst_offset = 25 if out_x > in_x else -25
                dpg.draw_line(
                    (out_x + dst_offset * 2, out_y),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_line(
                    (out_x + dst_offset * 2, in_y + 25),
                    (out_x + dst_offset * 2, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x + dst_offset, in_y + 25),
                    (out_x + dst_offset * 2, in_y + 25),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            elif isinstance(src_node, Conditional):
                in_x, in_y = dst_in_points[dst_ind]
                dpg.draw_line(
                    (in_x, out_y),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y),
                    (in_x, out_y),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            elif isinstance(dst_node, Connector):
                in_x, in_y = dst_in_points[dst_ind]
                dst_offset = 25 if out_x > in_x else -25
                dpg.draw_line(
                    (out_x, in_y + 25),
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2)
                dpg.draw_arrow(
                    (in_x + dst_offset, in_y + 25),
                    (out_x, in_y + 25),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)
            else:
                dpg.draw_arrow(
                    dst_in_points[dst_ind],
                    (out_x, out_y),
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)

    def redraw(self, parent: str, nodes: list[Node]):
        """Deletes the connection and draws a new version of it."""
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
        self.draw(parent, nodes)

    def delete(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
