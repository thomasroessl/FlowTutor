from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Tuple, Union
from uuid import uuid4
import dearpygui.dearpygui as dpg
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

from flowtutor.themes import theme_colors

if TYPE_CHECKING:
    from flowtutor.flowchart.connection import Connection

FLOWCHART_TAG = 'flowchart'


class Node(ABC):

    def __init__(self):
        self._tag = str(uuid4())
        self._connections: list[Connection] = []
        self._scope: list[str] = []
        self._pos = (0, 0)

    def __repr__(self) -> str:
        return f'({self.tag})'

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        self._tag = tag

    @property
    def scope(self) -> list[str]:
        return self._scope

    @scope.setter
    def scope(self, scope: list[str]):
        self._scope = scope

    @property
    def points(self) -> list[Tuple[int, int]]:
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
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, pos: Tuple[int, int]):
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
    def raw_in_points(self) -> list[Tuple[int, int]]:
        pass

    @property
    @abstractmethod
    def raw_out_points(self) -> list[Tuple[int, int]]:
        pass

    @property
    def in_points(self) -> list[Tuple[int, int]]:
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_in_points))

    @property
    def out_points(self) -> list[Tuple[int, int]]:
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_out_points))

    @property
    @abstractmethod
    def color(self):
        pass

    @property
    @abstractmethod
    def shape(self) -> list[Tuple[int, int]]:
        pass

    @property
    def connections(self) -> list[Connection]:
        return self._connections

    @connections.setter
    def connections(self, connections: list[Connection]):
        self._connections = connections

    def find_connection(self, index: int) -> Optional[Connection]:
        return next(filter(lambda c: c is not None and c.src_ind == index, self.connections), None)

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):
        color = self.color
        pos_x, pos_y = self.pos
        with dpg.draw_node(
                tag=self.tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]
            thickness = 3 if is_selected else 2 if self.is_hovered(
                mouse_pos) else 1
            if len(self.points) == 1:
                dpg.draw_circle(self.points[0], 25, fill=color)
                dpg.draw_circle(self.points[0], 25, color=text_color, thickness=thickness)
            else:
                dpg.draw_polygon(self.points, fill=color)
                dpg.draw_polygon(self.points, color=text_color, thickness=thickness)
                label = self.__class__.__name__
                text_width, text_height = dpg.get_text_size(label)
                dpg.draw_text((pos_x + self.width / 2 - text_width / 2, pos_y + self.height / 2 - text_height / 2),
                              label, color=(0, 0, 0), size=18)

        for connection in self.connections:
            connection.draw(self)

    def redraw(self, mouse_pos: Optional[Tuple[int, int]], selected_node):
        """Deletes the node and draws a new version of it."""
        self.delete()
        self.draw(mouse_pos, selected_node == self)

    def is_hovered(self, mouse_pos: Union[Tuple[int, int], None]):
        if mouse_pos is None:
            return False
        point = Point(*mouse_pos)
        if len(self.points) == 1:
            center = Point(*self.points[0])
            return point.distance(center) <= 25
        else:
            polygon = Polygon(self.points)
            return polygon.contains(point)

    def has_nested_nodes(self):
        return False

    def delete(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
