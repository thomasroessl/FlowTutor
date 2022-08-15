import dearpygui.dearpygui as dpg
import re
from shapely.geometry import Point

from modals import Modals
from node import Node
from connection import Connection
from conditional import Conditional
from connector import Connector


class FlowChart:

    nodes: list[Node] = []

    connections: list[Connection] = []

    hovered_add_button = None

    dragging_node: Node = None

    selected_node: Node = None

    # The offset of the currently dragging node to its origin before moving
    drag_offset: tuple[int, int] = (0, 0)

    # The size of the GUI parent
    parent_size: tuple[int, int] = (0, 0)

    mouse_position: tuple[int, int] = None

    mouse_position_on_canvas: tuple[int, int] = None

    def __init__(self, tag: str, width: int, height: int):
        self.width = width
        self.height = height
        self.tag = tag
        dpg.add_drawlist(tag=self.tag,
                         width=self.width,
                         height=self.height)
        with dpg.handler_registry():
            dpg.add_mouse_move_handler(callback=self.on_hover)
            dpg.add_mouse_drag_handler(callback=self.on_drag)
            dpg.add_mouse_click_handler(callback=self.on_mouse_click)
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)
            dpg.add_key_press_handler(
                dpg.mvKey_Delete, callback=self.on_delete_press)

    def on_hover(self, _, data: tuple[int, int]):
        """Sets the mouse poition variable and redraws all objects."""
        self.mouse_position = data
        if not dpg.is_item_hovered(self.tag):
            self.mouse_position_on_canvas = None
            return
        self.mouse_position_on_canvas = self.get_point_on_canvas(data)
        self.redraw_all()

    def on_drag(self):
        """Redraws the currently dragging node to its new position."""
        if self.mouse_position_on_canvas is None or self.dragging_node is None:
            return
        (cX, cY) = self.mouse_position_on_canvas
        (oX, oY) = self.drag_offset
        self.dragging_node.pos = (cX - oX, cY - oY)
        self.dragging_node.redraw(
            self.tag, self.mouse_position_on_canvas, self.selected_node, self.connections)

    def on_mouse_click(self):
        """Handles pressing down of the mouse button."""
        if self.mouse_position_on_canvas is None:
            return
        prev_selected_node = self.selected_node
        self.select_node(self.find_hovered_node())
        if self.hovered_add_button is not None:
            m = re.search('(.*)\[(.*)\]', self.hovered_add_button)
            connection_node_tag = m.group(1)
            connection_index = m.group(2)
            connection_node = self.find_node(connection_node_tag)
            _, connection_point_y = connection_node.out_points[
                int(connection_index)]
            if len(connection_node.out_points) == 2:
                if int(connection_index) == 0:
                    new_node_pos = [
                        connection_node.pos[0] - 125, connection_point_y + 80]
                else:
                    new_node_pos = [
                        connection_node.pos[0] + 125, connection_point_y + 80]
            else:
                new_node_pos = [
                    connection_node.pos[0], connection_point_y + 80]

            def callback(node):
                new_node_tag = self.add_node(node, new_node_pos)
                self.add_connection(connection_node_tag,
                                    connection_index, new_node_tag)
                self.redraw_all()
            Modals.show_node_type_modal(callback, self.mouse_position)
        elif self.selected_node is not None:
            self.dragging_node = self.selected_node
            (pX, pY) = self.dragging_node.pos
            (cX, cY) = self.mouse_position_on_canvas
            self.drag_offset = (cX - pX, cY - pY)
            self.dragging_node.redraw(
                self.tag, self.mouse_position_on_canvas, self.selected_node, self.connections)

        if prev_selected_node is not None:
            prev_selected_node.redraw(
                self.tag, self.mouse_position_on_canvas, self.selected_node, self.connections)

    def on_mouse_release(self):
        self.dragging_node = None
        self.resize()

    def on_delete_press(self):
        if self.selected_node is None or isinstance(self.select_node, Connector):
            return
        src_connections = self.selected_node.get_src_connections(
            self.connections)
        dst_connections = self.selected_node.get_dst_connections(
            self.connections)
        if len(src_connections) == 1 and len(dst_connections) == 1:
            self.remove_connection(src_connections[0])
            self.remove_connection(dst_connections[0])
            self.add_connection(
                dst_connections[0].src, dst_connections[0].index, src_connections[0].dst)
        elif len(src_connections) == 0 and len(dst_connections) == 1:
            self.remove_connection(dst_connections[0])
        elif len(src_connections) > 1:
            def callback():
                for child in self.get_node_children(self.selected_node):
                    self.remove_node(child)
                self.remove_node(self.selected_node)
                self.redraw_all()
                self.cleanup_connections()
                self.select_node(None)
            Modals.show_approval_modal(
                "Delete Node",
                "Deleting this node will also delete its children.",
                callback)
            return
        self.remove_node(self.selected_node)
        self.select_node(None)
        self.redraw_all()

    def redraw_all(self):
        self.hovered_add_button = None
        for connection in self.connections:
            connection.redraw(self.tag, self.nodes)
        is_add_button_drawn = False
        for node in self.nodes:
            # The currently draggingis skipped. It gets redrawn in on_drag.
            if node == self.dragging_node:
                continue
            node.redraw(self.tag, self.mouse_position_on_canvas,
                        self.selected_node, self.connections)
            if not is_add_button_drawn:
                is_add_button_drawn = self.draw_add_button(node)
        self.resize()

    def find_node(self, tag: str) -> Node:
        return next(filter(lambda n: n.tag == tag, self.nodes), None)

    def find_hovered_node(self):
        return next(filter(lambda n: n.is_hovered(
            self.mouse_position_on_canvas), self.nodes), None)

    def find_connection(self, src_tag: str, index: int):
        return next(filter(lambda c: c.src == src_tag and c.index == int(index), self.connections), None)

    def select_node(self, node: Node):
        self.selected_node = node
        dpg.configure_item(
            "selected_node", default_value=None if self.selected_node is None else self.selected_node.tag)

    def get_node_children(self, node: Node, cond_count: int = 0, connection_index: int = None):
        children: list[Node] = []
        if isinstance(node, Conditional):
            cond_count += 1
        for connection in filter(lambda c: c.src == node.tag and (connection_index is None or c.index == connection_index), self.connections):
            child = self.find_node(connection.dst)
            if isinstance(child, Connector):
                if cond_count == 1:
                    children.append(child)
                else:
                    children.extend(
                        [child, *self.get_node_children(child, cond_count - 1)])
            else:
                children.extend(
                    [child, *self.get_node_children(child, cond_count)])
        return children

    def cleanup_connections(self):
        self.connections = list(filter(lambda c: dpg.does_item_exist(c.src)
                                       and dpg.does_item_exist(c.dst), self.connections))

    def add_node(self, node: Node, pos: tuple[int, int]) -> str:
        node.pos = pos
        node.draw(self.tag, self.mouse_position_on_canvas, self.connections)
        self.nodes.append(node)
        if isinstance(node, Conditional):
            pos_x, pos_y = pos
            connector_node = Connector()
            self.add_node(connector_node,
                          (pos_x + node.width/2 - 25, pos_y + 100))
            self.nodes.append(connector_node)
            self.add_connection(node.tag, 0, connector_node.tag)
            self.add_connection(node.tag, 1, connector_node.tag)
        return node.tag

    def add_connection(self, src_tag: str, index: int, dst_tag: str):
        existing_connection = self.find_connection(src_tag, index)
        """If there is already a connection on this position, an additional connection is added"""
        if existing_connection is not None:
            self.move_children(src_tag, int(index), 135)
            self.remove_connection(existing_connection)
            existing_additional_connection = self.find_connection(dst_tag, 0)
            if existing_additional_connection is None:
                additional_connection = Connection(
                    dst_tag, 0, existing_connection.dst)
                self.connections.append(additional_connection)
            else:
                additional_connection = Connection(
                    existing_additional_connection.dst, 0, existing_connection.dst)
                self.connections.append(additional_connection)
        new_connection = Connection(src_tag, int(index), dst_tag)
        self.connections.append(new_connection)

    def remove_node(self, node: Node):
        if node is None:
            return
        node.delete()
        if self.nodes.__contains__(node):
            self.nodes.remove(node)

    def remove_connection(self, connection: Connection):
        if connection is None:
            return
        connection.delete()
        self.connections.remove(connection)

    def move_children(self, node_tag: str, connection_index: int, dist: int):
        node = self.find_node(node_tag)
        if node is None:
            return
        for child in self.get_node_children(node, 0, connection_index):
            pos_x, pos_y = child.pos
            child.pos = (pos_x, pos_y + dist)
            child.redraw(self.tag, self.mouse_position_on_canvas,
                         self.selected_node, self.connections)
        self.resize()

    def draw_add_button(self, node: Node):
        """Draws a Symbol for adding connected nodes, if the mouse is over a connection point.
           Returns True if an add button was drawn.
        """
        close_point = None
        if self.mouse_position_on_canvas is not None:
            close_point = next(
                filter(
                    lambda p: Point(p).distance(Point(self.mouse_position_on_canvas)) < 12, node.out_points), None)
        if close_point is not None:
            with dpg.draw_node(parent=node.tag):
                dpg.draw_circle(close_point, 12, fill=(255, 255, 255))
                x, y = close_point
                dpg.draw_text((x - 6.5, y - 15), "+",
                              color=(0, 0, 0), size=29)
                self.hovered_add_button = f"{node.tag}[{node.out_points.index(close_point)}]"
            return True
        return False

    def resize(self):
        """Sets the size of the drawing area."""
        width, height = self.parent_size

        for node in self.nodes:
            (_, _, max_x, max_y) = node.bounds
            if max_x + 16 > width:
                width = max_x + 16
            if max_y + 16 > height:
                height = max_y + 16
        dpg.set_item_height(self.tag, height-16)
        dpg.set_item_width(self.tag, width-16)

    def get_point_on_canvas(self, point_on_screen: tuple[int, int]):
        """Maps the point in screen coordinates to canvas coordinates."""
        offsetX, offsetY = dpg.get_item_rect_min(self.tag)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
