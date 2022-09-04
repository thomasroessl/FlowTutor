import re
from typing import Optional
import dearpygui.dearpygui as dpg
import os
from shapely.geometry import Point
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.root import Root
from flowtutor.settings import Settings
from flowtutor.themes import create_theme_dark, create_theme_light
from flowtutor.modals import Modals
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.connector import Connector

FLOWCHART_TAG = 'flowchart'


class GUI:

    hovered_add_button: Optional[str] = None

    dragging_node: Optional[Node] = None

    selected_node: Optional[Node] = None

    # The offset of the currently dragging node to its origin before moving
    drag_offset: tuple[int, int] = (0, 0)

    # The size of the GUI parent
    parent_size: tuple[int, int] = (0, 0)

    mouse_position: Optional[tuple[int, int]] = None

    mouse_position_on_canvas: Optional[tuple[int, int]] = None

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.flowchart = Flowchart()

        dpg.create_context()

        with dpg.font_registry():
            deafault_font = dpg.add_font(os.path.join(os.path.dirname(__file__), '../../assets/inconsolata.ttf'), 18)
        dpg.bind_font(deafault_font)

        with dpg.viewport_menu_bar(tag='menu_bar'):
            with dpg.menu(label='File'):
                dpg.add_menu_item(label='Save')
                dpg.add_menu_item(label='Save As')
            with dpg.menu(label='View'):
                with dpg.menu(label='Theme'):
                    dpg.add_menu_item(label='Light', callback=self.on_light_theme_menu_item_click)
                    dpg.add_menu_item(label='Dark', callback=self.on_dark_theme_menu_item_click)
            with dpg.menu(label='Help'):
                dpg.add_menu_item(label='About')

        with dpg.window(tag='main_window'):
            with dpg.group(tag='main_group', pos=[7, 30], horizontal=True):
                with dpg.child_window(width=217, label='Selected Node'):
                    dpg.add_text('Selected Node:')
                    dpg.add_text('None', tag='selected_node')

        with dpg.item_handler_registry(tag='window_handler'):
            dpg.add_item_resize_handler(callback=self.on_window_resize)
        dpg.bind_item_handler_registry('main_window', 'window_handler')

        dpg.configure_app()

        dpg.create_viewport(
            title='FlowTutor',
            width=int(Settings.get_setting('width', 1000)),
            height=int(Settings.get_setting('height', 1000)))

        if Settings.get_setting('theme', 'light') == 'light':
            dpg.bind_theme(create_theme_light())
        else:
            dpg.bind_theme(create_theme_dark())

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('main_window', True)

        with dpg.child_window(tag='flowchart_container', parent='main_group', horizontal_scrollbar=True):
            dpg.add_drawlist(tag=FLOWCHART_TAG,
                             width=self.width,
                             height=self.height)

            with dpg.handler_registry():
                dpg.add_mouse_move_handler(callback=self.on_hover)
                dpg.add_mouse_drag_handler(callback=self.on_drag)
                dpg.add_mouse_click_handler(callback=self.on_mouse_click)
                dpg.add_mouse_release_handler(callback=self.on_mouse_release)
                dpg.add_key_press_handler(
                    dpg.mvKey_Delete, callback=self.on_delete_press)

    def on_light_theme_menu_item_click(self):
        dpg.bind_theme(create_theme_light())
        self.redraw_all()
        Settings.set_setting('theme', 'light')

    def on_dark_theme_menu_item_click(self):
        dpg.bind_theme(create_theme_dark())
        self.redraw_all()
        Settings.set_setting('theme', 'dark')

    def on_window_resize(self):
        self.parent_size = dpg.get_item_rect_size('flowchart_container')
        self.resize()
        Settings.set_setting('height', dpg.get_viewport_height())
        Settings.set_setting('width', dpg.get_viewport_width())
        pass

    def on_hover(self, _, data: tuple[int, int]):
        '''Sets the mouse poition variable and redraws all objects.'''
        self.mouse_position = data
        if not dpg.is_item_hovered(FLOWCHART_TAG):
            self.mouse_position_on_canvas = None
            return
        self.mouse_position_on_canvas = self.get_point_on_canvas(data)
        self.redraw_all()

    def on_drag(self):
        '''Redraws the currently dragging node to its new position.'''
        if self.mouse_position_on_canvas is None or self.dragging_node is None:
            return
        (cX, cY) = self.mouse_position_on_canvas
        (oX, oY) = self.drag_offset
        self.dragging_node.pos = (cX - oX, cY - oY)
        self.dragging_node.redraw(self.mouse_position_on_canvas, self.selected_node)

    def on_mouse_click(self):
        '''Handles pressing down of the mouse button.'''
        if self.mouse_position_on_canvas is None:
            return
        prev_selected_node = self.selected_node
        self.select_node(self.flowchart.find_hovered_node(self.mouse_position_on_canvas))
        if self.hovered_add_button is not None:
            m = re.search(r'(.*)\[(.*)\]', self.hovered_add_button)
            if m is not None:
                parent_tag = m.group(1)
                src_index = m.group(2)
                parent = self.flowchart.find_node(parent_tag)

            def callback(node):
                if parent is not None:
                    self.flowchart.add_node(parent, node, int(src_index))
                    self.redraw_all()
            Modals.show_node_type_modal(callback, self.mouse_position)
        elif self.selected_node is not None:
            self.dragging_node = self.selected_node
            (pX, pY) = self.dragging_node.pos
            (cX, cY) = self.mouse_position_on_canvas
            self.drag_offset = (cX - pX, cY - pY)
            self.dragging_node.redraw(self.mouse_position_on_canvas, self.selected_node)

        if prev_selected_node is not None:
            prev_selected_node.redraw(self.mouse_position_on_canvas, self.selected_node)

    def on_mouse_release(self):
        self.dragging_node = None
        self.resize()

    def on_delete_press(self):
        if self.selected_node is None or isinstance(self.select_node, Connector) or isinstance(self.select_node, Root):
            return
        # def callback():
        #     self.flowchart.remove_node(self.selected_node)
        #     self.select_node(None)
        #     self.redraw_all()

        # if self.selected_node.has_child:
        #     Modals.show_approval_modal(
        #         'Delete Node',
        #         'Deleting this node will also delete its children.',
        #         callback)
        # else:
        #     callback()

    def select_node(self, node: Optional[Node]):
        self.selected_node = node
        dpg.configure_item(
            'selected_node', default_value=None if self.selected_node is None else self.selected_node.tag)

    def redraw_all(self):
        self.hovered_add_button = None
        is_add_button_drawn = False
        for node in self.flowchart:
            # The currently draggingis skipped. It gets redrawn in on_drag.
            if node == self.dragging_node:
                continue
            node.redraw(self.mouse_position_on_canvas, self.selected_node)
            if not is_add_button_drawn:
                is_add_button_drawn = self.draw_add_button(node)
        self.resize()

    def draw_add_button(self, node: Node):
        '''Draws a Symbol for adding connected nodes, if the mouse is over a connection point.
           Returns True if an add button was drawn.
        '''
        close_point = None
        if self.mouse_position_on_canvas is not None:
            close_point = next(
                filter(
                    lambda p: Point(p).distance(Point(self.mouse_position_on_canvas)) < 12, node.out_points), None)
        if close_point is not None:
            with dpg.draw_node(parent=node.tag):
                dpg.draw_circle(close_point, 12, fill=(255, 255, 255))
                dpg.draw_circle(close_point, 12, color=(0, 0, 0))
                x, y = close_point
                dpg.draw_text((x - 5.5, y - 12), '+',
                              color=(0, 0, 0), size=24)
                src_ind = node.out_points.index(close_point)
                self.hovered_add_button = f'{node.tag}[{src_ind}]'
            return True
        return False

    def resize(self):
        '''Sets the size of the drawing area.'''
        width, height = self.parent_size

        for node in self.flowchart:
            (_, _, max_x, max_y) = node.bounds
            if max_x + 16 > width:
                width = max_x + 16
            if max_y + 16 > height:
                height = max_y + 16
        dpg.set_item_height(FLOWCHART_TAG, height-16)
        dpg.set_item_width(FLOWCHART_TAG, width-16)

    def get_point_on_canvas(self, point_on_screen: tuple[int, int]):
        '''Maps the point in screen coordinates to canvas coordinates.'''
        offsetX, offsetY = dpg.get_item_rect_min(FLOWCHART_TAG)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
