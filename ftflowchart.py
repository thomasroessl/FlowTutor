import dearpygui.dearpygui as dpg
import re
from operator import itemgetter
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from ftnodetype import FTNodeType
from ftmodals import FTModals
from ftshapes import FTShapes


class FTFlowChart:

    nodes = []

    connections = []

    hovered_node = None

    hovered_connector = None

    dragging_node = None

    selected_node = None

    node_index = 0

    # The offset of the currently dragging node to its origin before moving
    drag_offset = (0, 0)

    # The size of the GUI parent
    parent_size = (0, 0)

    mouse_position = None

    mouse_position_on_canvas = None

    def __init__(self, tag, width, height):
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

    def get_point_on_canvas(self, point_on_screen):
        """Maps the point in screen coordinates to canvas coordinates."""
        offsetX, offsetY = dpg.get_item_rect_min(self.tag)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)

    def redraw_all(self):
        self.hovered_connector = None
        for connection in self.connections:
            self.redraw_connection(connection)
        is_connector_drawn = False
        for node in self.nodes:
            # The currently draggingis skipped. It gets redrawn in on_drag.
            if node == self.dragging_node:
                self.hovered_node = node
                continue
            node_data = dpg.get_item_user_data(node)
            if self.is_node_hovered(node_data, self.mouse_position_on_canvas):
                self.hovered_node = node
            self.redraw_node(node, node_data)
            if not is_connector_drawn:
                is_connector_drawn = self.draw_connector(node, node_data)

    def on_hover(self, _, data):
        """Sets the mouse poition variable and redraws all objects."""
        self.mouse_position = data

        if not dpg.is_item_hovered(self.tag):
            self.mouse_position_on_canvas = None
            return

        self.mouse_position_on_canvas = self.get_point_on_canvas(data)

        self.hovered_node = None
        self.redraw_all()

    def on_drag(self):
        """Redraws the currently dragging node to its new position."""
        if self.mouse_position_on_canvas is None or self.dragging_node is None:
            return
        (cX, cY) = self.mouse_position_on_canvas
        (oX, oY) = self.drag_offset
        self.redraw_node(self.dragging_node, pos=(cX - oX, cY - oY))

    def on_mouse_click(self):
        """Handles pressing down of the mouse button."""
        if self.mouse_position_on_canvas is None:
            return

        prev_selected_node = self.selected_node

        self.selected_node = self.hovered_node

        dpg.configure_item("selected_node", default_value=self.selected_node)

        if self.hovered_connector is not None:
            m = re.search('(.*)\[(.*)\]', self.hovered_connector)
            connection_node = m.group(1)
            connection_index = m.group(2)
            connection_node_data = dpg.get_item_user_data(connection_node)
            connection_node_pos, connection_node_out_points = itemgetter(
                "pos", "out_points")(connection_node_data)
            _, connection_point_y = connection_node_out_points[
                int(connection_index)]
            if len(connection_node_out_points) == 2:
                if int(connection_index) == 0:
                    new_node_pos = [
                        connection_node_pos[0] - 125, connection_point_y + 80]
                else:
                    new_node_pos = [
                        connection_node_pos[0] + 125, connection_point_y + 80]
            else:
                new_node_pos = [
                    connection_node_pos[0], connection_point_y + 80]

            def assignment_callback():
                new_node = self.add_node(
                    FTNodeType.Assignment, new_node_pos)
                self.add_connection(
                    connection_node, connection_index, new_node)

            def contitional_callback():
                new_node = self.add_node(
                    FTNodeType.Conditional, new_node_pos)
                self.add_connection(
                    connection_node, connection_index, new_node)

            def loop_callback():
                new_node = self.add_node(FTNodeType.Loop, new_node_pos)
                self.add_connection(
                    connection_node, connection_index, new_node)

            def input_callback():
                new_node = self.add_node(FTNodeType.Input, new_node_pos)
                self.add_connection(
                    connection_node, connection_index, new_node)

            def output_callback():
                new_node = self.add_node(FTNodeType.Output, new_node_pos)
                self.add_connection(
                    connection_node, connection_index, new_node)

            FTModals.show_node_type_modal(
                assignment_callback, contitional_callback, loop_callback, input_callback, output_callback, self.mouse_position)

        elif self.hovered_node is not None:
            node_data = dpg.get_item_user_data(self.hovered_node)
            self.dragging_node = self.hovered_node
            (pX, pY) = node_data["pos"]
            (cX, cY) = self.mouse_position_on_canvas
            self.drag_offset = (cX - pX, cY - pY)
            self.redraw_node(self.hovered_node, node_data)

        self.redraw_node(prev_selected_node)

    def get_node_children(self, node_tag, connection_index=None):
        children = []
        for connection in filter(lambda c: c["src"] == node_tag and (connection_index is None or c["index"] == connection_index), self.connections):
            child = connection["dst"]
            children.extend([child, *self.get_node_children(child)])
        return children

    def on_mouse_release(self):
        self.dragging_node = None
        self.resize()

    def on_delete_press(self):
        if self.selected_node is None:
            return

        src_connections = self.get_src_connections(self.selected_node)
        dst_connections = self.get_dst_connections(self.selected_node)

        if len(src_connections) == 1 and len(dst_connections) == 1:
            self.remove_connection(src_connections[0])
            self.remove_connection(dst_connections[0])
            self.add_connection(
                dst_connections[0]["src"], dst_connections[0]["index"], src_connections[0]["dst"])
        elif len(src_connections) == 0 and len(dst_connections) == 1:
            self.remove_connection(dst_connections[0])
        elif len(src_connections) > 1:
            def callback():
                for child in self.get_node_children(self.selected_node):
                    self.remove_node(child)
                self.remove_node(self.selected_node)
                self.redraw_all()
                self.cleanup_connections()
            FTModals.show_approval_modal(
                "Delete Node",
                "Deleting this node will also delete its children.",
                callback)
            return

        self.remove_node(self.selected_node)

        self.selected_node = None

        self.redraw_all()

    def cleanup_connections(self):
        self.connections = list(filter(lambda c: dpg.does_item_exist(
            c["src"]) and dpg.does_item_exist(c["dst"]), self.connections))

    def add_node(self, type, pos):
        self.node_index += 1
        tag = f"node{self.node_index}"
        self.nodes.append(tag)
        self.draw_node(tag, type, pos)
        return tag

    def remove_node(self, tag):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
        self.nodes.remove(tag)

    def add_connection(self, src, index, dst):

        existing_connection = next(
            filter(
                lambda c: c["src"] == src and c["index"] == int(index), self.connections), None)

        if existing_connection is not None:
            self.move_children(src, int(index), 135)
            self.remove_connection(existing_connection)
            additional_connection = {
                "src": dst,
                "index": 0,
                "dst": existing_connection["dst"]
            }
            self.connections.append(additional_connection)
            self.draw_connection(additional_connection)

        new_connection = {
            "src": src,
            "index": int(index),
            "dst": dst
        }
        self.connections.append(new_connection)
        self.draw_connection(new_connection)
        self.redraw_all()

    def move_children(self, node_tag, connection_index, dist):
        for child in self.get_node_children(node_tag, connection_index):
            node_data = dpg.get_item_user_data(child)
            (pX, pY) = node_data["pos"]
            self.redraw_node(child, node_data, (pX, pY + dist))

    def remove_connection(self, connection):
        if connection is None:
            return
        src, index, dst = itemgetter("src", "index", "dst")(connection)
        tag = f"{src}[{index}]->{dst}"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
        self.connections.remove(connection)

    def get_src_connections(self, node_tag):
        """Returns all connections with the node as source."""
        return [c for c in self.connections if c["src"] == node_tag]

    def get_dst_connections(self, node_tag):
        """Returns all connections with the node as destination."""
        return [c for c in self.connections if c["dst"] == node_tag]

    def is_node_hovered(self, node_data, pos):
        if pos is None:
            return False
        points = node_data["points"]
        point = Point(*pos)
        polygon = Polygon(points)
        return polygon.contains(point)

    def redraw_node(self, tag, node_data=None, pos=None):
        """Deletes a node and draws a new version of it."""
        if not dpg.does_item_exist(tag):
            return
        if tag is None:
            return
        if node_data is None:
            node_data = dpg.get_item_user_data(tag)
        if pos is None:
            pos = node_data["pos"]
        dpg.delete_item(tag)
        self.draw_node(tag, node_data["type"], pos)

    def redraw_connection(self, connection):
        """Deletes a connection and draws a new version of it."""
        if connection is None:
            return
        src, index, dst = itemgetter("src", "index", "dst")(connection)
        tag = f"{src}[{index}]->{dst}"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
            self.draw_connection(connection)

    def draw_connection(self, connection):
        """Draws a connection between two nodes."""
        src, index, dst = itemgetter("src", "index", "dst")(connection)
        if not dpg.does_item_exist(src) or not dpg.does_item_exist(dst):
            return
        src_data = dpg.get_item_user_data(src)
        dst_data = dpg.get_item_user_data(dst)

        dst_in_points: list = dst_data["in_points"]
        src_out_points: list = src_data["out_points"]

        with dpg.draw_node(
                tag=f"{src}[{index}]->{dst}",
                parent=self.tag):
            if len(src_out_points) == 2:
                out_x, out_y = src_out_points[int(index)]
                in_x, in_y = dst_in_points[0]
                if int(index) == 0:
                    dpg.draw_line(
                        (out_x - 50, out_y),
                        src_out_points[int(index)],
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
                        src_out_points[int(index)],
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
                    src_out_points[int(index)],
                    color=(255, 255, 255),
                    thickness=2,
                    size=10)

    def draw_node(self, tag, type, pos):
        pos_x, pos_y = pos
        width = 0
        height = 0
        points = []
        in_points = []
        out_points = []
        border_color = text_color = (255, 255, 255)

        if type == FTNodeType.Assignment:
            width = 150
            height = 75
            points = FTShapes.get_assignment_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (255, 255, 170)
        elif type == FTNodeType.Conditional:
            width = 150
            height = 100
            points = FTShapes.get_conditional_points()
            in_points = [(75, 0)]
            out_points = [(0, 50), (150, 50)]
            border_color = text_color = (255, 170, 170)
        elif type == FTNodeType.Loop:
            width = 150
            height = 75
            points = FTShapes.get_loop_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (255, 208, 147)
        elif type == FTNodeType.Input:
            width = 150
            height = 75
            points = FTShapes.get_input_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (147, 171, 255)
        elif type == FTNodeType.Output:
            width = 150
            height = 75
            points = FTShapes.get_output_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (147, 255, 149)
            pass

        points = list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), points))
        in_points = list(
            map(lambda p: (p[0] + pos_x, p[1] + pos_y), in_points))
        out_points = list(
            map(lambda p: (p[0] + pos_x, p[1] + pos_y), out_points))

        if tag == self.selected_node:
            border_color = (21, 151, 236)
        elif tag == self.hovered_node:
            border_color = (0, 119, 200)

        with dpg.draw_node(
                tag=tag,
                parent=self.tag,
                user_data={
                    "type": type,
                    "points": points,
                    "pos": pos,
                    "bounds": Polygon(points).bounds,
                    "in_points": in_points,
                    "out_points": out_points
                }):
            dpg.draw_polygon(points, color=border_color, thickness=2)
            text_width, text_height = dpg.get_text_size(tag)
            dpg.draw_text((pos_x + width / 2 - text_width / 2, pos_y + height / 2 - text_height / 2),
                          tag, color=text_color, size=18)

    def draw_connector(self, node_tag, node_data):
        """Draws a Symbol for adding connected nodes, if the mouse is over a connection point.
           Returns True if a connector was drawn.
        """
        out_points = node_data["out_points"]
        close_point = None
        if self.mouse_position_on_canvas is not None:
            close_point = next(
                filter(
                    lambda p: Point(p).distance(Point(self.mouse_position_on_canvas)) < 12, out_points), None)
        if close_point is not None:
            with dpg.draw_node(
                    tag="connector",
                    parent=node_tag):
                dpg.draw_circle(close_point, 12, fill=(255, 255, 255))
                x, y = close_point
                dpg.draw_text((x - 6.5, y - 15), "+",
                              color=(0, 0, 0), size=29)
                self.hovered_connector = f"{node_tag}[{out_points.index(close_point)}]"
            return True
        return False

    def resize(self):
        """Sets the size of the drawing area."""
        width, height = self.parent_size

        for node in self.nodes:
            node_data = dpg.get_item_user_data(node)
            (_, _, max_x, max_y) = node_data["bounds"]
            if max_x + 16 > width:
                width = max_x + 16
            if max_y + 16 > height:
                height = max_y + 16
        dpg.set_item_height(self.tag, height-16)
        dpg.set_item_width(self.tag, width-16)
