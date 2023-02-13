from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Tuple, Union
from uuid import uuid4
import dearpygui.dearpygui as dpg
from shapely.geometry import Polygon
from shapely.geometry import Point

from flowtutor.gui.themes import theme_colors

if TYPE_CHECKING:
    from flowtutor.flowchart.connection import Connection

FLOWCHART_TAG = 'flowchart'


class Node(ABC):

    def __init__(self):
        self._tag = str(uuid4())
        self._connections: list[Connection] = []
        self._scope: list[str] = []
        self._pos = (0, 0)
        self._comment = ''
        self._break_point = False
        self._lines = []
        self._has_debug_cursor = False

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
    def shape(self) -> Polygon:  # pragma: no cover
        pos_x, pos_y = self.pos

        delta = self.width - self.shape_width

        if delta > 0:
            points = []
            for p in self.shape_points:
                x, y = p
                if x < self.shape_width / 2:
                    points.append((x - delta//2, y))
                elif x > self.shape_width / 2:
                    points.append((x + delta//2, y))
                else:
                    points.append((x, y))
        else:
            points = self.shape_points.copy()

        return Polygon(list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), points)))

    @property
    def width(self) -> int:
        label_width, _ = dpg.get_text_size(self.label)
        return int(max(self.shape_width, label_width + 40))

    @property
    @abstractmethod
    def shape_width(self) -> int:
        pass

    @property
    @abstractmethod
    def shape_height(self) -> int:
        pass

    @property
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, pos: Tuple[int, int]):
        self._pos = pos

    @property
    def bounds(self):
        return self.shape.bounds

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
    def lines(self) -> list[int]:
        return self._lines

    @lines.setter
    def lines(self, lines: list[int]):
        self._lines = lines

    @property
    def has_debug_cursor(self) -> bool:
        return self._has_debug_cursor

    @has_debug_cursor.setter
    def has_debug_cursor(self, has_debug_cursor: bool):
        self._has_debug_cursor = has_debug_cursor

    @property
    @abstractmethod
    def color(self):
        pass

    @property
    @abstractmethod
    def shape_points(self) -> list[Tuple[int, int]]:
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        pass

    @property
    def connections(self) -> list[Connection]:
        return self._connections

    @connections.setter
    def connections(self, connections: list[Connection]):
        self._connections = connections

    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        pass

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        self._comment = comment

    @property
    def break_point(self) -> bool:
        return self._break_point

    @break_point.setter
    def break_point(self, break_point: bool):
        self._break_point = break_point

    def get_left_x(self):
        return self.shape_width//2 - self.width//2

    def get_right_x(self):
        return (self.width + self.shape_width)//2

    def find_connection(self, index: int) -> Optional[Connection]:
        return next(filter(lambda c: c is not None and c.src_ind == index, self.connections), None)

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):  # pragma: no cover
        color = self.color
        pos_x, pos_y = self.pos
        with dpg.draw_node(
                tag=self.tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]
            thickness = 3 if is_selected else 2 if self.is_hovered(
                mouse_pos) else 1

            dpg.draw_polygon(list(self.shape.exterior.coords),
                             fill=color)
            dpg.draw_polygon(list(self.shape.exterior.coords),
                             color=(255, 0, 0) if self.break_point else text_color,
                             thickness=thickness)

            text_width, text_height = dpg.get_text_size(self.label)
            dpg.draw_text((pos_x + self.shape_width / 2 - text_width / 2,
                           pos_y + self.shape_height / 2 - text_height / 2),
                          self.label, color=(0, 0, 0), size=18)

            if self.has_debug_cursor:
                cursor_pos = self.pos
                cursor_pos_x, cursor_pos_y = cursor_pos
                dpg.draw_polygon([
                    cursor_pos,
                    (cursor_pos_x - 15, cursor_pos_y + 15),
                    (cursor_pos_x - 15, cursor_pos_y + 5),
                    (cursor_pos_x - 30, cursor_pos_y + 5),
                    (cursor_pos_x - 30, cursor_pos_y - 5),
                    (cursor_pos_x - 15, cursor_pos_y - 5),
                    (cursor_pos_x - 15, cursor_pos_y - 15),
                    cursor_pos
                ],
                    fill=(0, 255, 0))
                dpg.draw_polygon([
                    cursor_pos,
                    (cursor_pos_x - 15, cursor_pos_y + 15),
                    (cursor_pos_x - 15, cursor_pos_y + 5),
                    (cursor_pos_x - 30, cursor_pos_y + 5),
                    (cursor_pos_x - 30, cursor_pos_y - 5),
                    (cursor_pos_x - 15, cursor_pos_y - 5),
                    (cursor_pos_x - 15, cursor_pos_y - 15),
                    cursor_pos
                ],
                    color=text_color)

        for connection in self.connections:
            connection.draw(self)

    def redraw(self, mouse_pos: Optional[Tuple[int, int]], selected_node):
        '''Deletes the node and draws a new version of it.'''
        self.delete()
        self.draw(mouse_pos, selected_node == self)

    def is_hovered(self, mouse_pos: Union[Tuple[int, int], None]):
        if mouse_pos is None:
            return False
        point = Point(*mouse_pos)
        return self.shape.contains(point)

    def has_nested_nodes(self):
        return False

    def delete(self):  # pragma: no cover
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
