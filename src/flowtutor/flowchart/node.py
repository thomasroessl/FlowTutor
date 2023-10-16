from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, cast
from uuid import uuid4
import dearpygui.dearpygui as dpg
from shapely.geometry import Polygon

if TYPE_CHECKING:
    from flowtutor.flowchart.connection import Connection
    from flowtutor.flowchart.flowchart import Flowchart

FLOWCHART_TAG = 'flowchart'


class Node(ABC):
    '''The base class for all flowchart nodes.'''

    def __init__(self) -> None:
        self._tag = str(uuid4())
        self._shape_data: list[list[tuple[float, float]]] = []
        self._connections: list[Connection] = []
        self._scope: list[str] = []
        self._pos = (0, 0)
        self._comment = ''
        self._break_point = False
        self._is_comment = False
        self._needs_refresh = False
        self._is_hovered = False
        self._lines: list[int] = []
        self._has_debug_cursor = False

    def __repr__(self) -> str:
        return f'({self.tag}: {self.__class__.__name__})'

    @property
    def tag(self) -> str:
        '''The dearpygui tag for access to the drawn item.'''
        return self._tag

    @tag.setter
    def tag(self, tag: str) -> None:
        self._tag = tag

    @property
    def scope(self) -> list[str]:
        '''A list of predecessor node tags.

        This node is inside the scope of the predecessor, e.g. inside a loop body.
        '''
        return self._scope

    @scope.setter
    def scope(self, scope: list[str]) -> None:
        self._scope = scope

    @property
    def shape(self) -> Polygon:
        '''The shape of the node that gets drawn.'''
        return Polygon(self.transform_shape_points(self.shape_data[0]))

    def transform_shape_points(self,
                               shape_points: list[tuple[float, float]])\
            -> list[tuple[float, float]]:  # pragma: no cover
        '''Transforms the vertices of the shape polygon, so they are at the correct position globally.

        Also stretches the shape to accommodate the label text.

        Parameters:
            shape-points (list[tuple[float, float]]): The vertices of the shape polygon.
        '''
        pos_x, pos_y = self.pos

        # Difference between the label with and the shape polygon width.
        delta = self.width - self.shape_width

        if delta > 0:
            points = []
            for p in shape_points:
                x, y = p
                # Stretches the shape points, if the label text would be too long.
                if x < self.shape_width / 2:
                    points.append((x - delta//2, y))
                elif x > self.shape_width / 2:
                    points.append((x + delta//2, y))
                else:
                    points.append((x, y))
        else:
            points = shape_points.copy()
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), points))

    @property
    def width(self) -> int:
        '''The width of the shape when it's drawn.'''
        label_width, _ = dpg.get_text_size(self.label)
        return int(max(self.shape_width, label_width + 40))

    @property
    @abstractmethod
    def shape_width(self) -> int:
        '''The width of the polygon defined by the shape definition.'''
        pass

    @property
    @abstractmethod
    def shape_height(self) -> int:
        '''The height of the polygon defined by the shape definition.'''
        pass

    @property
    def pos(self) -> tuple[int, int]:
        '''The coordinates of the position of the node in the drawing space.'''
        return self._pos

    @pos.setter
    def pos(self, pos: tuple[int, int]) -> None:
        self._pos = pos

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        '''The minimum bounding region of the node shape.'''
        result: tuple[int, int, int, int] = self.shape.bounds
        return result

    @property
    @abstractmethod
    def raw_in_points(self) -> list[tuple[float, float]]:
        '''A list of points where the flowchart enters the node.

        Must be transformed to account for positioning of the node.'''
        pass

    @property
    @abstractmethod
    def raw_out_points(self) -> list[tuple[float, float]]:
        '''A list of points where the flowchart exits the node.

        Must be transformed to account for positioning of the node.'''
        pass

    @property
    def in_points(self) -> list[tuple[float, float]]:
        '''A list of points where the flowchart enters the node.'''
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_in_points))

    @property
    def out_points(self) -> list[tuple[float, float]]:
        '''A list of points where the flowchart exits the node.'''
        pos_x, pos_y = self.pos
        return list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), self.raw_out_points))

    @property
    def lines(self) -> list[int]:
        '''A list of line numbers corresponding to lines in the generated source code.'''
        return self._lines

    @lines.setter
    def lines(self, lines: list[int]) -> None:
        self._lines = lines

    @property
    def has_debug_cursor(self) -> bool:
        '''True if the debug cursor is on the node.'''
        return self._has_debug_cursor

    @has_debug_cursor.setter
    def has_debug_cursor(self, has_debug_cursor: bool) -> None:
        self._has_debug_cursor = has_debug_cursor

    @property
    @abstractmethod
    def color(self) -> tuple[int, int, int]:
        '''The color of the drawn node.'''
        pass

    @property
    def shape_data(self) -> list[list[tuple[float, float]]]:
        '''A list of shape vertex lists.

        Discontinuous lines are multiple vertex lists.'''
        return self._shape_data

    @property
    @abstractmethod
    def label(self) -> str:
        '''The text on the drawn node.'''
        pass

    @property
    def connections(self) -> list[Connection]:
        '''A list of connections to other nodes.'''
        return self._connections

    @connections.setter
    def connections(self, connections: list[Connection]) -> None:
        self._connections = connections

    @property
    @abstractmethod
    def is_initialized(self) -> bool:
        '''True if the user has entered all required parameters for the node.'''
        pass

    @property
    def comment(self) -> str:
        '''A source code comment for the user.'''
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        self._comment = comment

    @property
    def break_point(self) -> bool:
        '''True if there is a break point on the node.'''
        return self._break_point

    @break_point.setter
    def break_point(self, break_point: bool) -> None:
        self._break_point = break_point

    @property
    def is_comment(self) -> bool:
        '''True if the node is disabled with a comment.'''
        return self._is_comment

    @is_comment.setter
    def is_comment(self, is_comment: bool) -> None:
        self._is_comment = is_comment

    @property
    def needs_refresh(self) -> bool:
        '''True if the the node should be redrawn on the next render loop.'''
        return self._needs_refresh

    @needs_refresh.setter
    def needs_refresh(self, needs_refresh: bool) -> None:
        self._needs_refresh = needs_refresh

    @property
    def is_hovered(self) -> bool:
        '''True if the node should be dran in a hovered state.'''
        return self._is_hovered

    @is_hovered.setter
    def is_hovered(self, is_hovered: bool) -> None:
        self._is_hovered = is_hovered

    def get_disabled_inherited(self, flowchart: Optional[Flowchart]) -> bool:
        '''Checks if a predecessor of the node is disabled with a comment.

        Parameters:
            flowchart (Flowchart): The flowchart that contains the node.
        '''
        if not flowchart:
            return False
        containing_node = flowchart.find_containing_node(self)
        if not containing_node:
            return False
        return containing_node.is_comment or containing_node.get_disabled_inherited(flowchart)

    def get_left_x(self) -> int:
        '''Gets the x coordinate of the leftmost point of the bounding box of the shape.'''
        return self.shape_width//2 - self.width//2

    def get_right_x(self) -> int:
        '''Gets the x coordinate of the rightmost point of the bounding box of the shape.'''
        return (self.width + self.shape_width)//2

    def find_connection(self, index: int) -> Optional[Connection]:
        '''Find a connection on a specific connection index.

        Parameters:
            indes (int): The connection index, that should be found.'''
        return next(filter(lambda c: c is not None and c.src_ind == index, self.connections), None)

    def draw(self,
             flowchart: Flowchart,
             text_color: tuple[int, int, int, int],
             is_selected: bool = False) -> None:  # pragma: no cover
        '''Draws the node in the dearpygui drawing area.

        Parameters:
            flowchart (Flowchart): The flowchart that contains the node.
            text_color (tuple[int, int, int, int]): The color of the drawn text.
            is_selected (bool): True if the node should be drawn in a selected state.
        '''
        # Draw the node in grey, if it is disabled.
        color = (150, 150, 150) if self.is_comment or self.get_disabled_inherited(flowchart) else self.color

        pos_x, pos_y = self.pos
        with dpg.draw_node(
                tag=self.tag,
                parent=FLOWCHART_TAG):

            # Make the borders thicker if the node is in a selected state.
            thickness = 3 if is_selected else 2 if self.is_hovered else 1

            if self.shape_data:
                dpg.draw_polygon(self.transform_shape_points(self.shape_data[0]),
                                 fill=color)
                for shape in self.shape_data:
                    dpg.draw_polygon(self.transform_shape_points(shape),
                                     color=(255, 0, 0) if self.break_point else text_color,
                                     thickness=thickness)
            else:
                dpg.draw_polygon(list(self.shape.exterior.coords),
                                 fill=color)
                dpg.draw_polygon(list(self.shape.exterior.coords),
                                 color=(255, 0, 0) if self.break_point else text_color,
                                 thickness=thickness)

            text_width, text_height = dpg.get_text_size(self.label)

            # For a post-loop template node, draw an extra circle and shift the node down accordingly.
            if self.__class__.__name__ == 'Template' and cast(Any, self).control_flow == 'post-loop':
                dpg.draw_circle((pos_x + 75, pos_y + 25), 25, fill=self.color)
                dpg.draw_circle((pos_x + 75, pos_y + 25), 25, thickness=2, color=text_color)
                dpg.draw_text((pos_x + self.shape_width / 2 - text_width / 2,
                               pos_y + self.shape_height + 60 - text_height / 2),
                              self.label, color=(0, 0, 0), size=18)
            else:
                dpg.draw_text((pos_x + self.shape_width / 2 - text_width / 2,
                               pos_y + self.shape_height / 2 - text_height / 2),
                              self.label, color=(0, 0, 0), size=18)

            # If the node has the debug cursor, draw an arrow indicating this.
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
            connection.draw(text_color, self)

    def redraw(self, flowchart: Flowchart, selected_nodes: list[Node], text_color: tuple[int, int, int, int]) -> None:
        '''Deletes the node and draws a new version of it.

        Parameters:
            flowchart (Flowchart): The flowchart that contains the node.
            selected_nodes (list[Node]): A list of the selected nodes.
            text_color (tuple[int, int, int, int]): The color of the drawn text.
        '''
        self.delete()
        self.draw(flowchart, text_color, self in selected_nodes)

    def delete(self) -> None:  # pragma: no cover
        '''Deletes the drawn instance of the node from the drawing area.'''
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
