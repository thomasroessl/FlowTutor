from abc import ABC, abstractmethod
from uuid import uuid4
import dearpygui.dearpygui as dpg
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from nodetype import NodeType


class Node(ABC):

    def __init__(self, tag=None):
        if tag is None:
            self.tag = str(uuid4())
        else:
            self.tag = tag

    @property
    @abstractmethod
    def type(self) -> NodeType:
        pass

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        self._tag = tag

    @property
    def points(self) -> list[tuple[int, int]]:
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.shape))

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, pos: tuple[int, int]):
        self._pos = pos

    @property
    def bounds(self):
        if len(self.points) == 1:
            c_x, c_y = self.points[0]
            return (c_x - 25, c_y - 25, c_x + 25, c_y + 25)
        else:
            return Polygon(self.points).bounds

    @property
    @abstractmethod
    def raw_in_points(self) -> list[tuple[int, int]]:
        pass

    @property
    @abstractmethod
    def raw_out_points(self) -> list[tuple[int, int]]:
        pass

    @property
    def in_points(self) -> list[tuple[int, int]]:
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_in_points))

    @property
    def out_points(self) -> list[tuple[int, int]]:
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_out_points))

    @property
    @abstractmethod
    def color(self):
        pass

    @property
    @abstractmethod
    def shape(self) -> list[tuple[int, int]]:
        pass

    def draw(self, parent: str, mouse_pos: tuple, connections, is_selected=False):
        color = self.color
        pos_x, pos_y = self.pos
        with dpg.draw_node(
                tag=self.tag,
                parent=parent):
            thickness = 4 if is_selected else 3 if self.is_hovered(
                mouse_pos) else 2
            if len(self.points) == 1:
                dpg.draw_circle(self.points[0], 25,
                                color=color, thickness=thickness)
            else:
                dpg.draw_polygon(self.points, color=color, thickness=thickness)
                label = str(self.type).split(".")[1]
                text_width, text_height = dpg.get_text_size(label)
                dpg.draw_text((pos_x + self.width / 2 - text_width / 2, pos_y + self.height / 2 - text_height / 2),
                              label, color=color, size=18)

    def redraw(self, parent: str, mouse_pos: tuple[int, int], selected_node, connections):
        """Deletes the node and draws a new version of it."""
        self.delete()
        self.draw(parent, mouse_pos, connections, selected_node == self)

    def is_hovered(self, mouse_pos: tuple[int, int]):
        if mouse_pos is None:
            return False
        point = Point(*mouse_pos)
        if len(self.points) == 1:
            center = Point(*self.points[0])
            return point.distance(center) <= 25
        else:
            polygon = Polygon(self.points)
            return polygon.contains(point)

    def get_src_connections(self, connections):
        """Returns all connections with the node as source."""
        return [c for c in connections if c.src == self.tag]

    def get_dst_connections(self, connections):
        """Returns all connections with the node as destination."""
        return [c for c in connections if c.dst == self.tag]

    def delete(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
