import dearpygui.dearpygui as dpg
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from operator import itemgetter

from shapetype import ShapeType


class FlowChart:

    shapes = []

    connections = []

    hovered_shape = None

    dragging_shape = None

    selected_shape = None

    # The offset of the currently dragging shape to its origin before moving
    drag_offset = (0, 0)

    # The size of the GUI parent
    parent_size = (0, 0)

    mouse_position_on_canvas = None

    @staticmethod
    def get_assignment_points():
        return [
            (0, 0),
            (150, 0),
            (150, 75),
            (0, 75),
            (0, 0)
        ]

    @staticmethod
    def get_conditional_points():
        return [
            (75, 0),
            (0, 50),
            (75, 100),
            (150, 50),
            (75, 0)
        ]

    @staticmethod
    def get_loop_points():
        return [
            (0, 37.5),
            (20, 75),
            (130, 75),
            (150, 37.5),
            (130, 0),
            (20, 0),
            (0, 37.5)
        ]

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

    def get_point_on_canvas(self, point_on_screen):
        """Maps the point in screen coordinates to canvas coordinates."""
        offsetX, offsetY = dpg.get_item_rect_min(self.tag)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)

    def on_hover(self, _, data):
        """Sets the mouse poition variable and redraws all objects."""
        if not dpg.is_item_hovered(self.tag):
            self.mouse_position_on_canvas = None
            return

        self.mouse_position_on_canvas = self.get_point_on_canvas(data)

        self.hovered_shape = None

        for shape in self.shapes:
            # The currently draggingis skipped. It gets redrawn in on_drag.
            if shape == self.dragging_shape:
                self.hovered_shape = shape
                continue
            shape_data = dpg.get_item_user_data(shape)
            if self.is_shape_hovered(shape_data, self.mouse_position_on_canvas):
                self.hovered_shape = shape
            self.redraw_shape(shape, shape_data)

        for connection in self.connections:
            self.redraw_connection(connection)

    def on_drag(self):
        """Redraws the currently dragging shape to its new position."""
        if self.mouse_position_on_canvas is None or self.dragging_shape is None:
            return
        (cX, cY) = self.mouse_position_on_canvas
        (oX, oY) = self.drag_offset
        self.redraw_shape(self.dragging_shape, pos=(cX - oX, cY - oY))

    def on_mouse_click(self):
        """Handles pressing down of the mouse button."""
        if self.mouse_position_on_canvas is None:
            return

        prev_selected_shape = self.selected_shape

        self.selected_shape = self.hovered_shape

        if self.hovered_shape is not None:
            shape_data = dpg.get_item_user_data(self.hovered_shape)
            self.dragging_shape = self.hovered_shape
            (pX, pY) = shape_data["pos"]
            (cX, cY) = self.mouse_position_on_canvas
            self.drag_offset = (cX - pX, cY - pY)
            self.redraw_shape(self.hovered_shape, shape_data)

        self.redraw_shape(prev_selected_shape)

    def on_mouse_release(self):
        self.dragging_shape = None
        self.resize()

    def add_shape(self, type, pos):
        tag = f"shape{len(self.shapes) + 1}"
        self.shapes.append(tag)
        self.draw_shape(tag, type, pos)
        return tag

    def add_connection(self, src, dst):
        connection = {
            "src": src,
            "dst": dst
        }
        self.connections.append(connection)
        self.draw_connection(connection)

    def is_shape_hovered(self, shape_data, pos):
        points = shape_data["points"]
        point = Point(*pos)
        polygon = Polygon(points)
        return polygon.contains(point)

    def redraw_shape(self, tag, shape_data=None, pos=None):
        """Deletes a shape and draws a new version of it."""
        if tag is None:
            return
        if shape_data is None:
            shape_data = dpg.get_item_user_data(tag)
        if pos is None:
            pos = shape_data["pos"]
        dpg.delete_item(tag)
        self.draw_shape(tag, shape_data["type"], pos)

    def redraw_connection(self, connection):
        """Deletes a connection and draws a new version of it."""
        if connection is None:
            return
        src, dst = itemgetter("src", "dst")(connection)
        tag = f"{src}->{dst}"
        dpg.delete_item(tag)
        self.draw_connection(connection)

    def draw_connection(self, connection):
        """Draws a connection between two shapes."""
        src, dst = itemgetter("src", "dst")(connection)
        src_data = dpg.get_item_user_data(src)
        dst_data = dpg.get_item_user_data(dst)

        dst_in_points: list = dst_data["in_points"]
        src_out_points: list = src_data["out_points"]

        with dpg.draw_node(
                tag=f"{src}->{dst}",
                parent=self.tag):
            if len(src_out_points) == 2:
                out_x, out_y = src_out_points[0]
                in_x, in_y = dst_in_points[0]
                dpg.draw_line(
                    (in_x, out_y), 
                    src_out_points[0], 
                    color=(255, 255, 255), 
                    thickness=2)
                dpg.draw_arrow(
                    (in_x, in_y), 
                    (in_x, out_y), 
                    color=(255, 255, 255), 
                    thickness=2, 
                    size=10)
            else:
                dpg.draw_arrow(
                    dst_in_points[0], 
                    src_out_points[0], 
                    color=(255, 255, 255), 
                    thickness=2, 
                    size=10)
                pass

        pass

    def draw_shape(self, tag, type, pos):
        pos_x, pos_y = pos
        width = 0
        height = 0
        points = []
        in_points = []
        out_points = []
        border_color = text_color = (255, 255, 255)

        if type == ShapeType.Assignment:
            width = 150
            height = 75
            points = FlowChart.get_assignment_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (255, 255, 170)
        elif type == ShapeType.Conditional:
            width = 150
            height = 100
            points = FlowChart.get_conditional_points()
            in_points = [(75, 0)]
            out_points = [(0, 50), (150, 50)]
            border_color = text_color = (255, 170, 170)
        elif type == ShapeType.Loop:
            width = 150
            height = 75
            points = FlowChart.get_loop_points()
            in_points = [(75, 0)]
            out_points = [(75, 75)]
            border_color = text_color = (255, 208, 147)
        elif type == ShapeType.Input:
            pass
        elif type == ShapeType.Output:
            pass

        points = list(map(lambda p: (p[0] + pos_x, p[1] + pos_y), points))
        in_points = list(
            map(lambda p: (p[0] + pos_x, p[1] + pos_y), in_points))
        out_points = list(
            map(lambda p: (p[0] + pos_x, p[1] + pos_y), out_points))

        if tag == self.selected_shape:
            border_color = (21, 151, 236)
        elif tag == self.hovered_shape:
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

    def resize(self):
        """Sets the size of the drawing area."""
        width, height = self.parent_size

        for shape in self.shapes:
            shape_data = dpg.get_item_user_data(shape)
            (_, _, max_x, max_y) = shape_data["bounds"]
            if max_x + 16 > width:
                width = max_x + 16
            if max_y + 16 > height:
                height = max_y + 16
        dpg.set_item_height(self.tag, height-16)
        dpg.set_item_width(self.tag, width-16)

    def get_max_y(self):
        """Returns the larges y value of all shapes."""
        max_y = 0
        for shape in self.shapes:
            shape_data = dpg.get_item_user_data(shape)
            for _, y in shape_data["points"]:
                if y > max_y:
                    max_y = y
        return max_y
