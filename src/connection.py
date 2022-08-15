import dearpygui.dearpygui as dpg

from node import Node


class Connection:

    def __init__(self, src: str, index: int, dst: str):
        self._src = src
        self._index = index
        self._dst = dst

    @property
    def tag(self) -> str:
        return f"{self.src}[{self.index}]->{self.dst}"

    @property
    def src(self) -> str:
        return self._src

    @property
    def index(self) -> int:
        return self._index

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

        with dpg.draw_node(
                tag=self.tag,
                parent=parent):
            if len(src_out_points) == 2:
                out_x, out_y = src_out_points[int(self.index)]
                in_x, in_y = dst_in_points[0]
                if int(self.index) == 0:
                    dpg.draw_line(
                        (out_x - 50, out_y),
                        src_out_points[int(self.index)],
                        color=(255, 255, 255),
                        thickness=2)
                    dpg.draw_arrow(
                        (in_x, in_y),
                        (out_x - 50, out_y),
                        color=(255, 255, 255),
                        thickness=2,
                        size=10)
                else:
                    dpg.draw_line(
                        (out_x + 50, out_y),
                        src_out_points[int(self.index)],
                        color=(255, 255, 255),
                        thickness=2)
                    dpg.draw_arrow(
                        (in_x, in_y),
                        (out_x + 50, out_y),
                        color=(255, 255, 255),
                        thickness=2,
                        size=10)
            else:
                dpg.draw_arrow(
                    dst_in_points[0],
                    src_out_points[int(self.index)],
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
