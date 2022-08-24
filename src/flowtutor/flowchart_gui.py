from typing import Optional
import dearpygui.dearpygui as dpg
import re
from shapely.geometry import Point

from flowtutor.modals import Modals
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.connection import Connection
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.loop import Loop


class FlowChartGUI:

    nodes: list[Node] = []

    connections: list[Connection] = []

    hovered_add_button: Optional[str] = None

    dragging_node: Optional[Node] = None

    selected_node: Optional[Node] = None

    # The offset of the currently dragging node to its origin before moving
    drag_offset: tuple[int, int] = (0, 0)

    # The size of the GUI parent
    parent_size: tuple[int, int] = (0, 0)

    mouse_position: Optional[tuple[int, int]] = None

    mouse_position_on_canvas: Optional[tuple[int, int]] = None

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
            m = re.search(r'(.*)\[(.*)\]\[(.*)\]', self.hovered_add_button)
            if m is not None:
                parent_tag = m.group(1)
                src_index = m.group(2)
                dst_index = m.group(3)
                parent = self.find_node(parent_tag)

            def callback(node):
                self.add_node(node, parent, int(src_index), int(dst_index))
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
                dst_connections[0].src, dst_connections[0].src_ind, src_connections[0].dst, src_connections[0].dst_ind)
        elif len(src_connections) == 0 and len(dst_connections) == 1:
            self.remove_connection(dst_connections[0])
        elif len(src_connections) > 1:
            def callback():
                if self.selected_node is not None:
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

    def find_node(self, tag: str) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.tag == tag, self.nodes), None)

    def find_hovered_node(self):
        return next(filter(lambda n: n.is_hovered(
            self.mouse_position_on_canvas), self.nodes), None)

    def find_connection(self, src_tag: str, index: int):
        return next(filter(lambda c: c.src == src_tag and c.src_ind == int(index), self.connections), None)

    def select_node(self, node: Optional[Node]):
        self.selected_node = node
        dpg.configure_item(
            "selected_node", default_value=None if self.selected_node is None else self.selected_node.tag)

    def get_node_children(self, node: Node, cond_count: int = 0, connection_index: Optional[int] = None):
        children: list[Node] = []
        if isinstance(node, Conditional):
            cond_count += 1
        for connection in filter(lambda c: c.src != c.dst and c.src == node.tag
                                 and (connection_index is None or c.src_ind == connection_index), self.connections):
            child = self.find_node(connection.dst)
            if isinstance(child, Connector):
                if cond_count == 1:
                    children.append(child)
                else:
                    children.extend(
                        [child, *self.get_node_children(child, cond_count - 1)])
            elif child is not None:
                children.extend(
                    [child, *self.get_node_children(child, cond_count)])
        return children

    def cleanup_connections(self):
        self.connections = list(filter(lambda c: dpg.does_item_exist(c.src)
                                       and dpg.does_item_exist(c.dst), self.connections))

    def add_node(self, node: Node, parent: Optional[Node], src_ind: int = 0, dst_ind: int = 0):
        if parent is None:
            pos = (135, 20)
        elif isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.width/2 - 25), int(pos_y + 180))
        else:
            _, connection_point_y = parent.out_points[int(src_ind)]
            if isinstance(parent, Conditional):
                if int(src_ind) == 0:
                    pos = (parent.pos[0] - 125, connection_point_y + 80)
                else:
                    pos = (parent.pos[0] + 125, connection_point_y + 80)
            elif isinstance(parent, Loop) and int(src_ind) == 1:
                pos = (parent.pos[0] + 145, connection_point_y + 80)
            else:
                pos = (parent.pos[0], connection_point_y + 80)
        node.pos = pos
        node.draw(self.tag, self.mouse_position_on_canvas, self.connections)
        self.nodes.append(node)
        self.move_below(node)
        if isinstance(node, Conditional):
            connector_node = Connector()
            self.add_node(connector_node, node)
            self.nodes.append(connector_node)
            self.add_connection(node.tag, 0, connector_node.tag, 0)
            self.add_connection(node.tag, 1, connector_node.tag, 0)
        elif isinstance(node, Loop):
            self.add_connection(node.tag, 1, node.tag, 1)
        if not isinstance(node, Connector) and parent is not None:
            self.add_connection(parent.tag, src_ind, node.tag, int(dst_ind))

    def add_connection(self, src_tag: str, src_ind: int, dst_tag: str, dst_ind: int):
        existing_connection = self.find_connection(src_tag, src_ind)
        """If there is already a connection on this position, an additional connection is added"""
        if existing_connection is not None:
            self.remove_connection(existing_connection)
            existing_additional_connection = self.find_connection(dst_tag, 0)
            if existing_additional_connection is None:
                additional_connection = Connection(
                    dst_tag, 0, existing_connection.dst, existing_connection.dst_ind)
                self.connections.append(additional_connection)
            else:
                additional_connection = Connection(
                    existing_additional_connection.dst, 0, existing_connection.dst, existing_connection.dst_ind)
                self.connections.append(additional_connection)
        new_connection = Connection(src_tag, int(src_ind), dst_tag, int(dst_ind))
        self.connections.append(new_connection)

    def remove_node(self, node: Optional[Node]):
        if node is None:
            return
        node.delete()
        if self.nodes.__contains__(node):
            self.nodes.remove(node)

    def remove_connection(self, connection: Optional[Connection]):
        if connection is None:
            return
        connection.delete()
        self.connections.remove(connection)

    def move_below(self, node: Optional[Node]):
        if node is None:
            return
        for node_below in [n for n in self.nodes if n.pos[1] > node.pos[1]]:
            pos_x, pos_y = node_below.pos
            node_below.pos = (pos_x, int(pos_y + node.height / 2 + 20))
        self.redraw_all()

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
                src_ind = node.out_points.index(close_point)
                dst_ind = 1 if isinstance(node, Loop) and src_ind == 1 else 0
                self.hovered_add_button = f"{node.tag}[{src_ind}][{dst_ind}]"
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
