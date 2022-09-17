from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple
import re
import os.path
import dearpygui.dearpygui as dpg
from shapely.geometry import Point

from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.output import Output
from flowtutor.settings import Settings
from flowtutor.themes import create_theme_dark, create_theme_light
from flowtutor.modals import Modals

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'


class GUI:

    hovered_add_button: Optional[str] = None

    dragging_node: Optional[Node] = None

    selected_node: Optional[Node] = None

    # The offset of the currently dragging node to its origin before moving
    drag_offset: Tuple[int, int] = (0, 0)

    # The size of the GUI parent
    parent_size: Tuple[int, int] = (0, 0)

    mouse_position: Optional[Tuple[int, int]] = None

    mouse_position_on_canvas: Optional[Tuple[int, int]] = None

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.flowchart = Flowchart()

        dpg.create_context()

        c_image_width, c_image_height, _, c_image_data = dpg.load_image(
            os.path.join(os.path.dirname(__file__), '../../assets/c.png'))
        python_image_width, python_image_height, _, python_image_data = dpg.load_image(
            os.path.join(os.path.dirname(__file__), '../../assets/python.png'))

        with dpg.texture_registry():
            dpg.add_static_texture(width=c_image_width, height=c_image_height,
                                   default_value=c_image_data, tag="c_image")
            dpg.add_static_texture(width=python_image_width, height=python_image_height,
                                   default_value=python_image_data, tag="python_image")

        with dpg.font_registry():
            deafault_font = dpg.add_font(os.path.join(os.path.dirname(__file__), '../../assets/inconsolata.ttf'), 18)
        dpg.bind_font(deafault_font)

        with dpg.viewport_menu_bar(tag='menu_bar'):
            with dpg.menu(label='File'):
                dpg.add_menu_item(label='Open...')
                dpg.add_separator()
                dpg.add_menu_item(label='Save')
                dpg.add_menu_item(label='Save As...')
            with dpg.menu(label='View'):
                with dpg.menu(label='Theme'):
                    dpg.add_menu_item(label='Light', callback=self.on_light_theme_menu_item_click)
                    dpg.add_menu_item(label='Dark', callback=self.on_dark_theme_menu_item_click)
            with dpg.menu(label='Help'):
                dpg.add_menu_item(label='About')

        with dpg.window(tag='main_window'):
            with dpg.group(tag='main_group', horizontal=True):
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_any', show=True):
                    with dpg.menu_bar():
                        dpg.add_text('Selected Node')
                    dpg.add_text('None', tag='selected_any_name')
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_assignment', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Assignment')
                    with dpg.group(horizontal=True):
                        dpg.add_text('Name')
                        dpg.add_input_text(tag='selected_assignment_name', indent=50, width=-1, no_spaces=True,
                                           callback=lambda _, data: (self.selected_node.__setattr__('var_name', data),
                                                                     self.redraw_all()))
                    with dpg.group(horizontal=True):
                        dpg.add_text('Value')
                        dpg.add_input_text(tag='selected_assignment_value', indent=50, width=-1,
                                           callback=lambda _, data: (self.selected_node.__setattr__('var_value', data),
                                                                     self.redraw_all()))
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_declaration', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Declaration')
                    with dpg.group(horizontal=True):
                        dpg.add_text('Name')
                        dpg.add_input_text(tag='selected_declaration_name', indent=50, width=-1, no_spaces=True,
                                           callback=lambda _, data: (self.selected_node.__setattr__('var_name', data),
                                                                     self.redraw_all()))
                    with dpg.group(horizontal=True):
                        dpg.add_text('Type')
                        dpg.add_combo(['Integer', 'Float', 'String'],
                                      tag='selected_declaration_type', indent=50, width=-1,
                                      callback=lambda _, data: self.selected_node.__setattr__('var_type', data))
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_conditional', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Conditional')
                    with dpg.group():
                        dpg.add_text('Condition')
                        dpg.add_input_text(tag='selected_conditional_condition', width=-1,
                                           callback=lambda _, data: (self.selected_node.__setattr__('condition', data),
                                                                     self.redraw_all()))
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_loop', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Loop')
                    with dpg.group():
                        dpg.add_text('Condition')
                        dpg.add_input_text(tag='selected_loop_condition', width=-1,
                                           callback=lambda _, data: (self.selected_node.__setattr__('condition', data),
                                                                     self.redraw_all()))
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_input', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Input')
                    with dpg.group(horizontal=True):
                        dpg.add_text('Name')
                        dpg.add_input_text(tag='selected_input_name', indent=50, width=-1, no_spaces=True,
                                           callback=lambda _, data: (self.selected_node.__setattr__('var_name', data),
                                                                     self.redraw_all()))
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, tag='selected_output', show=False):
                    with dpg.menu_bar():
                        dpg.add_text('Output')
                    with dpg.group():
                        dpg.add_text('Expression')
                        dpg.add_input_text(tag='selected_output_expression', width=-1,
                                           callback=lambda _, data: (self.selected_node.__setattr__('expression', data),
                                                                     self.redraw_all()))

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
            if self.flowchart.lang == 'c':
                dpg.add_image('c_image', pos=(10, 10))
            elif self.flowchart.lang == 'python':
                dpg.add_image('python_image', pos=(10, 10))
            
            with dpg.handler_registry():
                dpg.add_mouse_move_handler(callback=self.on_hover)
                dpg.add_mouse_drag_handler(callback=self.on_drag)
                dpg.add_mouse_click_handler(callback=self.on_mouse_click)
                dpg.add_mouse_release_handler(callback=self.on_mouse_release)
                dpg.add_key_press_handler(
                    dpg.mvKey_Delete, callback=self.on_delete_press)

    def on_select_node(self, node: Optional[Node]):
        self.selected_node = node
        dpg.hide_item('selected_any')
        dpg.hide_item('selected_assignment')
        dpg.hide_item('selected_declaration')
        dpg.hide_item('selected_conditional')
        dpg.hide_item('selected_loop')
        dpg.hide_item('selected_input')
        dpg.hide_item('selected_output')
        if isinstance(self.selected_node, Assignment):
            dpg.configure_item('selected_assignment_name', default_value=self.selected_node.var_name)
            dpg.configure_item('selected_assignment_value', default_value=self.selected_node.var_value)
            dpg.show_item('selected_assignment')
        elif isinstance(self.selected_node, Declaration):
            dpg.configure_item('selected_declaration_name', default_value=self.selected_node.var_name)
            dpg.configure_item('selected_declaration_type', default_value=self.selected_node.var_type)
            dpg.show_item('selected_declaration')
        elif isinstance(self.selected_node, Conditional):
            dpg.configure_item('selected_conditional_condition', default_value=self.selected_node.condition)
            dpg.show_item('selected_conditional')
        elif isinstance(self.selected_node, Loop):
            dpg.configure_item('selected_loop_condition', default_value=self.selected_node.condition)
            dpg.show_item('selected_loop')
        elif isinstance(self.selected_node, Input):
            dpg.configure_item('selected_input_name', default_value=self.selected_node.var_name)
            dpg.show_item('selected_input')
        elif isinstance(self.selected_node, Output):
            dpg.configure_item('selected_output_expression', default_value=self.selected_node.expression)
            dpg.show_item('selected_output')
        else:
            dpg.show_item('selected_any')
            if self.selected_node:
                selected_name = self.selected_node.__class__.__name__
            else:
                selected_name = 'None'
            dpg.configure_item('selected_any_name', default_value=selected_name)

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

    def on_hover(self, _, data: Tuple[int, int]):
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
        self.on_select_node(self.flowchart.find_hovered_node(self.mouse_position_on_canvas))
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
        if self.selected_node is None:
            return

        def callback():
            if self.selected_node is not None:
                self.flowchart.clear()
                self.flowchart.remove_node(self.selected_node)
                self.on_select_node(None)
                self.redraw_all()

        if self.selected_node.has_nested_nodes():
            Modals.show_approval_modal(
                'Delete Node',
                'Deleting this node will also delete all nested nodes.',
                callback)
        else:
            callback()

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

    def get_point_on_canvas(self, point_on_screen: Tuple[int, int]):
        '''Maps the point in screen coordinates to canvas coordinates.'''
        offsetX, offsetY = dpg.get_item_rect_min(FLOWCHART_TAG)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
