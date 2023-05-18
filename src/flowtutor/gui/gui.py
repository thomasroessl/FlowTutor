from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Type, Union, cast
import re
import os.path
import dearpygui.dearpygui as dpg
from shapely.geometry import Point
from blinker import signal
from pickle import dump, load
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet
from flowtutor.gui.section_node_extras import SectionNodeExtras
from flowtutor.gui.sidebar import Sidebar
from flowtutor.gui.sidebar_assignment import SidebarAssignment
from flowtutor.gui.sidebar_call import SidebarCall
from flowtutor.gui.sidebar_conditional import SidebarConditional
from flowtutor.gui.sidebar_declaration import SidebarDeclaration
from flowtutor.gui.sidebar_declarations import SidebarDeclarations
from flowtutor.gui.sidebar_dowhileloop import SidebarDoWhileLoop
from flowtutor.gui.sidebar_functionend import SidebarFunctionEnd
from flowtutor.gui.sidebar_input import SidebarInput
from flowtutor.gui.sidebar_forloop import SidebarForLoop
from flowtutor.gui.sidebar_none import SidebarNone
from flowtutor.gui.sidebar_whileloop import SidebarWhileLoop
from flowtutor.gui.sidebar_output import SidebarOutput
from flowtutor.gui.sidebar_snippet import SidebarSnippet
from flowtutor.gui.window_types import WindowTypes
from flowtutor.modal_service import ModalService
from flowtutor.settings_service import SettingsService
from flowtutor.codegenerator import CodeGenerator
from flowtutor.gui.debugger import Debugger
from flowtutor.gui.sidebar_functionstart import SidebarFunctionStart

from flowtutor.gui.themes import create_theme_dark, create_theme_light

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'
FLOWCHART_CONTAINER_TAG = 'flowchart_container'
SOURCE_CODE_TAG = 'source_code'
TAB_BAR_TAG = 'func_tab_bar'


class GUI:

    hovered_add_button: Optional[str] = None

    dragging_node: Optional[Node] = None

    selected_node: Optional[Node] = None

    # The offset of the currently dragging node to its origin before moving
    drag_offset: tuple[int, int] = (0, 0)

    # The size of the GUI parent
    parent_size: tuple[int, int] = (0, 0)

    declared_variables: list[dict[str, Any]] = []

    mouse_position: Optional[tuple[int, int]] = None

    mouse_position_on_canvas: Optional[tuple[int, int]] = None

    prev_source_code = ''

    debugger: Optional[Debugger] = None

    variable_table_id: Optional[int] = None

    selected_flowchart_name: str = 'main'

    sidebar_title_tag: Optional[str | int] = None

    file_path: Optional[str] = None

    sidebar_functionstart: Optional[SidebarFunctionStart] = None

    @property
    def selected_flowchart(self) -> Flowchart:
        return self.flowcharts[self.selected_flowchart_name]

    @inject
    def __init__(self,
                 width: int,
                 height: int,
                 code_generator: CodeGenerator = Provide['code_generator'],
                 modal_service: ModalService = Provide['modal_service'],
                 settings_service: SettingsService = Provide['settings_service']):
        self.width = width
        self.height = height
        self.code_generator = code_generator
        self.modal_service = modal_service
        self.settings_service = settings_service
        self.flowcharts = {
            'main': Flowchart('main')
        }

        signal('hit-line').connect(self.on_hit_line)
        signal('program-finished').connect(self.on_program_finished)
        signal('variables').connect(self.on_variables)

        dpg.create_context()

        for image in ['c', 'run', 'stop', 'step_into', 'step_over', 'hammer', 'trash', 'pencil']:
            image_width, image_height, _, image_data = dpg.load_image(
                os.path.join(os.path.dirname(__file__), f'../../../assets/{image}.png'))
            with dpg.texture_registry():
                dpg.add_static_texture(width=image_width, height=image_height,
                                       default_value=image_data, tag=f'{image}_image')

        with dpg.font_registry():
            default_font = dpg.add_font(os.path.join(os.path.dirname(__file__), '../../../assets/inconsolata.ttf'), 18)
            dpg.add_font(os.path.join(os.path.dirname(__file__),
                         '../../../assets/inconsolata.ttf'), 22, tag='header_font')
        dpg.bind_font(default_font)

        with dpg.viewport_menu_bar(tag='menu_bar'):
            with dpg.menu(label='File'):
                dpg.add_menu_item(label='New Program', callback=lambda: self.on_new(self))
                dpg.add_separator()
                dpg.add_menu_item(label='Open...', callback=lambda: self.on_open(self))
                dpg.add_separator()
                dpg.add_menu_item(label='Save', callback=lambda: self.on_save(self))
                dpg.add_menu_item(label='Save As...', callback=lambda: self.on_save_as(self))
            with dpg.menu(label='Edit'):
                dpg.add_menu_item(label='Add Function', callback=lambda: self.on_add_function(self))
                dpg.add_separator()
                dpg.add_menu_item(label='Clear Current Function', callback=lambda: self.on_clear(self))

            with dpg.menu(label='View'):
                with dpg.menu(label='Theme'):
                    dpg.add_menu_item(label='Light', callback=lambda: self.on_light_theme_menu_item_click(self))
                    dpg.add_menu_item(label='Dark', callback=lambda: self.on_dark_theme_menu_item_click(self))
            with dpg.menu(label='Help'):
                dpg.add_menu_item(label='About')

        with dpg.window(tag='main_window'):
            with dpg.group(tag='main_group', horizontal=True):
                with dpg.child_window(width=217, pos=[7, 30], menubar=True, show=True):

                    with dpg.menu_bar():
                        self.sidebar_title_tag = dpg.add_text('Program')
                        with dpg.group(tag='function_management_group', horizontal=True, show=False):
                            dpg.add_spacer(width=63)
                            self.rename_button = dpg.add_image_button('pencil_image')
                            self.delete_button = dpg.add_image_button('trash_image')
                        with dpg.theme() as tool_button_theme:
                            with dpg.theme_component(dpg.mvImageButton):
                                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 4, category=dpg.mvThemeCat_Core)

                        dpg.bind_item_theme(self.rename_button, tool_button_theme)
                        dpg.bind_item_theme(self.delete_button, tool_button_theme)

                    self.sidebar_none = SidebarNone(self)
                    self.sidebar_assignment = SidebarAssignment(self)
                    self.sidebar_function_start = SidebarFunctionStart(self)
                    self.sidebar_function_end = SidebarFunctionEnd(self)
                    self.sidebar_call = SidebarCall(self)
                    self.sidebar_declaration = SidebarDeclaration(self)
                    self.sidebar_declarations = SidebarDeclarations(self)
                    self.sidebar_conditional = SidebarConditional(self)
                    self.sidebar_for_loop = SidebarForLoop(self)
                    self.sidebar_while_loop = SidebarWhileLoop(self)
                    self.sidebar_do_while_loop = SidebarDoWhileLoop(self)
                    self.sidebar_input = SidebarInput(self)
                    self.sidebar_output = SidebarOutput(self)
                    self.sidebar_snippet = SidebarSnippet(self)

                    self.sidebars: dict[Union[Type[Node], Type[None]], Sidebar] = {
                        type(None): self.sidebar_none,
                        Assignment: self.sidebar_assignment,
                        FunctionStart: self.sidebar_function_start,
                        FunctionEnd: self.sidebar_function_end,
                        Call: self.sidebar_call,
                        Declaration: self.sidebar_declaration,
                        Declarations: self.sidebar_declarations,
                        Conditional: self.sidebar_conditional,
                        ForLoop: self.sidebar_for_loop,
                        WhileLoop: self.sidebar_while_loop,
                        DoWhileLoop: self.sidebar_do_while_loop,
                        Input: self.sidebar_input,
                        Output: self.sidebar_output,
                        Snippet: self.sidebar_snippet
                    }

                    self.window_types = WindowTypes(self)

                    self.section_node_extras = SectionNodeExtras(self)

        with dpg.item_handler_registry(tag='window_handler'):
            dpg.add_item_resize_handler(callback=lambda: self.on_window_resize(self))
        dpg.bind_item_handler_registry('main_window', 'window_handler')

        dpg.configure_app()

        dpg.create_viewport(
            title='FlowTutor',
            width=int(self.settings_service.get_setting('width', 1000) or 1000),
            height=int(self.settings_service.get_setting('height', 1000) or 1000))

        if self.settings_service.get_setting('theme', 'light') == 'light':
            dpg.bind_theme(create_theme_light())
        else:
            dpg.bind_theme(create_theme_dark())

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window('main_window', True)

        with dpg.child_window(parent='main_group', border=False, width=-1):
            with dpg.child_window(border=False, height=-254):
                with dpg.group(horizontal=True):
                    with dpg.group(width=-410):
                        with dpg.tab_bar(
                                tag=TAB_BAR_TAG,
                                reorderable=True,
                                callback=lambda _, tab: self.on_selected_tab_changed(self, _, tab)):
                            self.refresh_function_tabs()
                        with dpg.child_window(tag=FLOWCHART_CONTAINER_TAG, horizontal_scrollbar=True):

                            # Remove the padding of the flowchart container
                            with dpg.theme() as item_theme:
                                with dpg.theme_component(dpg.mvChildWindow):
                                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0.0, category=dpg.mvThemeCat_Core)
                            dpg.bind_item_theme(FLOWCHART_CONTAINER_TAG, item_theme)

                            dpg.add_drawlist(tag=FLOWCHART_TAG,
                                             width=self.width,
                                             height=self.height)
                            with dpg.handler_registry():
                                dpg.add_mouse_move_handler(callback=lambda _, data: self.on_hover(self, _, data))
                                dpg.add_mouse_drag_handler(callback=lambda: self.on_drag(self))
                                dpg.add_mouse_click_handler(callback=lambda: self.on_mouse_click(self))
                                dpg.add_mouse_release_handler(callback=lambda: self.on_mouse_release(self))
                                dpg.add_key_press_handler(
                                    dpg.mvKey_Delete, callback=lambda: self.on_delete_press(self))
                    with dpg.group(width=400):
                        dpg.add_input_text(tag=SOURCE_CODE_TAG, multiline=True, height=-1, readonly=True)
            with dpg.group(horizontal=True):
                with dpg.child_window(width=-410, border=False, height=250) as debugger_window:
                    self.debugger = Debugger(debugger_window)
                with dpg.child_window(width=400, border=False, height=250):
                    dpg.add_spacer(height=30)
                    dpg.add_text('Variables')
                    with dpg.table(header_row=True, row_background=True,
                                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                   borders_outerV=True, delay_search=True) as table_id:
                        self.variable_table_id = table_id
                        dpg.add_table_column(label='Name')
                        dpg.add_table_column(label='Value')

    def refresh_function_tabs(self) -> None:
        for tab in dpg.get_item_children(TAB_BAR_TAG)[1]:
            dpg.delete_item(tab)
        for func in self.flowcharts.keys():
            dpg.add_tab(label=func, user_data=func, parent=TAB_BAR_TAG)
        dpg.add_tab_button(label='+', callback=lambda: self.on_add_function(self), parent=TAB_BAR_TAG)

    @staticmethod
    def on_selected_tab_changed(self: GUI, _: Any, tab: Union[int, str]) -> None:
        self.clear_flowchart()
        self.selected_flowchart_name = dpg.get_item_user_data(tab)
        self.selected_node = self.selected_flowchart.root
        self.on_select_node(self.selected_flowchart.root)
        self.redraw_all()

    def on_hit_line(self, _: Any, **kw: int) -> None:
        line = kw['line']
        if self.debugger is not None:
            self.debugger.enable_all()
        for func in self.flowcharts.values():
            for node in func:
                node.has_debug_cursor = line in node.lines
                # Switches to the flowcharts, where the break point is hit
                if node.has_debug_cursor:
                    for tab in dpg.get_item_children(TAB_BAR_TAG)[1]:
                        if dpg.get_item_user_data(tab) == func.root.name:
                            dpg.set_value(TAB_BAR_TAG, tab)
        self.redraw_all()

    def on_variables(self, _: Any, **kw: dict[str, str]) -> None:
        variables = kw['variables']
        if self.debugger is not None:
            for row_id in dpg.get_item_children(self.variable_table_id)[1]:
                dpg.delete_item(row_id)
            if len(variables) > 0:
                for variable in variables:
                    with dpg.table_row(parent=self.variable_table_id):
                        dpg.add_text(variable)
                        dpg.add_text(variables[variable])
        self.redraw_all()

    def on_program_finished(self: GUI, _: Any, **kw: dict[str, str]) -> None:
        for flowchart in self.flowcharts.values():
            for node in flowchart:
                node.has_debug_cursor = False
        if self.debugger is not None:
            self.debugger.enable_build_and_run()
        self.redraw_all()

    @staticmethod
    def on_add_function(self: GUI) -> None:
        def callback(name: str) -> None:
            self.flowcharts[name] = Flowchart(name)
            self.refresh_function_tabs()
        i = len(self.flowcharts.values())
        new_name = f'fun_{i}'
        while new_name in self.flowcharts.keys():
            i += 1
            new_name = f'fun_{i}'
        self.modal_service.show_input_text_modal(
            'New Function',
            'Name',
            new_name,
            callback)

    def on_select_node(self, node: Optional[Node]) -> None:

        self.selected_node = node

        self.section_node_extras.toggle(node)

        [s.hide() for s in self.sidebars.values()]

        dpg.hide_item('function_management_group')

        sidebar = self.sidebars.get(type(node))
        if sidebar:
            sidebar.show(node)

    @staticmethod
    def on_open(self: GUI) -> None:
        def callback(file_path: str) -> None:
            with open(file_path, 'rb') as file:
                self.file_path = file_path
                dpg.set_viewport_title(f'FlowTutor - {file_path}')
                self.flowcharts = load(file)
                self.window_types.refresh()
                self.sidebar_none.refresh()
                self.redraw_all()
                self.refresh_function_tabs()
        self.modal_service.show_open_modal(callback)

    @staticmethod
    def on_new(self: GUI) -> None:
        def callback() -> None:
            self.file_path = None
            dpg.set_viewport_title('FlowTutor')
            self.clear_flowchart()
            self.flowcharts = {
                'main': Flowchart('main')
            }
            self.redraw_all()
            self.refresh_function_tabs()
        self.modal_service.show_approval_modal(
            'New Program', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    @staticmethod
    def on_clear(self: GUI) -> None:
        def callback() -> None:
            self.selected_flowchart.reset()
            self.clear_flowchart()
            self.redraw_all()
        self.modal_service.show_approval_modal(
            'Clear', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    @staticmethod
    def on_save(self: GUI) -> None:
        if self.file_path is not None:
            with open(self.file_path, 'wb') as file:
                dump(self.flowcharts, file)
        else:
            GUI.on_save_as(self)

    @staticmethod
    def on_save_as(self: GUI) -> None:
        def callback(file_path: str) -> None:
            with open(file_path, 'wb') as file:
                self.file_path = file_path
                dpg.set_viewport_title(f'FlowTutor - {file_path}')
                dump(self.flowcharts, file)
        self.modal_service.show_save_as_modal(callback)

    @staticmethod
    def on_light_theme_menu_item_click(self: GUI) -> None:
        dpg.bind_theme(create_theme_light())
        self.redraw_all()
        self.settings_service.set_setting('theme', 'light')

    @staticmethod
    def on_dark_theme_menu_item_click(self: GUI) -> None:
        dpg.bind_theme(create_theme_dark())
        self.redraw_all()
        self.settings_service.set_setting('theme', 'dark')

    @staticmethod
    def on_window_resize(self: GUI) -> None:
        (width, height) = dpg.get_item_rect_size(FLOWCHART_CONTAINER_TAG)
        self.parent_size = (width, height)
        self.resize()
        self.settings_service.set_setting('height', dpg.get_viewport_height())
        self.settings_service.set_setting('width', dpg.get_viewport_width())

    @staticmethod
    def on_hover(self: GUI, _: Any, data: tuple[int, int]) -> None:
        '''Sets the mouse poition variable and redraws all objects.'''
        self.mouse_position = data
        if not dpg.is_item_hovered(FLOWCHART_TAG):
            self.mouse_position_on_canvas = None
            return
        self.mouse_position_on_canvas = self.get_point_on_canvas(data)
        self.redraw_all()

    @staticmethod
    def on_drag(self: GUI) -> None:
        '''Redraws the currently dragging node to its new position.'''
        if self.mouse_position_on_canvas is None or self.dragging_node is None:
            return
        (cX, cY) = self.mouse_position_on_canvas
        (oX, oY) = self.drag_offset
        self.dragging_node.pos = (cX - oX, cY - oY)
        self.dragging_node.redraw(self.mouse_position_on_canvas, self.dragging_node)

    @staticmethod
    def on_mouse_click(self: GUI) -> None:
        '''Handles pressing down of the mouse button.'''
        if self.mouse_position_on_canvas is None:
            return
        prev_selected_node = self.selected_node
        self.on_select_node(self.selected_flowchart.find_hovered_node(self.mouse_position_on_canvas))
        if self.hovered_add_button is not None:
            m = re.search(r'(.*)\[(.*)\]', self.hovered_add_button)
            if m is not None:
                parent_tag = m.group(1)
                src_index = m.group(2)
                parent = self.selected_flowchart.find_node(parent_tag)

            def callback(node: Node) -> None:
                if parent is not None:
                    self.selected_flowchart.add_node(parent, node, int(src_index))
                    self.redraw_all()
                    self.resize()
            self.modal_service.show_node_type_modal(callback, self.mouse_position or (0, 0))
        elif self.selected_node is not None:
            self.dragging_node = self.selected_node
            (pX, pY) = self.dragging_node.pos
            (cX, cY) = self.mouse_position_on_canvas
            self.drag_offset = (cX - pX, cY - pY)
            self.dragging_node.redraw(self.mouse_position_on_canvas, self.selected_node)

        if prev_selected_node is not None:
            prev_selected_node.redraw(self.mouse_position_on_canvas, self.selected_node)

    @staticmethod
    def on_mouse_release(self: GUI) -> None:
        self.dragging_node = None
        self.resize()

    @staticmethod
    def on_delete_press(self: GUI) -> None:
        if self.selected_node is None:
            return

        def callback() -> None:
            if self.selected_node is not None:
                self.selected_flowchart.clear()
                self.selected_flowchart.remove_node(self.selected_node)
                self.on_select_node(None)
                self.redraw_all()
                self.resize()

        if self.selected_node.has_nested_nodes():
            self.modal_service.show_approval_modal(
                'Delete Node',
                'Deleting this node will also delete all nested nodes.',
                callback)
        else:
            callback()

    def set_sidebar_title(self, title: str) -> None:
        dpg.configure_item(self.sidebar_title_tag, default_value=title)

    def clear_flowchart(self) -> None:
        self.selected_node = None
        self.on_select_node(None)
        self.dragging_node = None
        for item in dpg.get_item_children(FLOWCHART_TAG)[2]:
            dpg.delete_item(item)

    def get_ordered_flowcharts(self) -> list[Flowchart]:
        '''Get a ordered list of flowcharts, by sorting the tabs by their x-position on screen.
           (workaround for missing feature in dearpygui)'''
        tabs = dpg.get_item_children(TAB_BAR_TAG)[1]
        filtered_tabs = list(filter(lambda tab: dpg.get_item_user_data(tab) is not None, tabs))
        # Put the tabs in a dictionary with their x-position as key
        converter = {}
        for tab in filtered_tabs:
            converter[dpg.get_item_rect_min(tab)[0]] = tab
        # Before initialization all tabs habe position (0, 0)
        # In this case, don't use the position for ordering
        if len(converter) != len(self.flowcharts):
            return list(self.flowcharts.values())
        pos = [dpg.get_item_rect_min(tab)[0] for tab in filtered_tabs]
        sortedPos = sorted(pos, key=lambda pos: cast(int, pos))
        return list(map(lambda x: self.flowcharts[dpg.get_item_user_data(converter[x])], sortedPos))

    def redraw_all(self) -> None:
        self.hovered_add_button = None
        is_add_button_drawn = False
        for node in self.selected_flowchart:
            # The currently draggingis skipped. It gets redrawn in on_drag.
            if node == self.dragging_node:
                continue
            node.redraw(self.mouse_position_on_canvas, self.selected_node)
            if not is_add_button_drawn:
                is_add_button_drawn = self.draw_add_button(node)
        if self.selected_flowchart.is_initialized():
            source_code = self.code_generator.write_source_files(self.get_ordered_flowcharts())
            if source_code is not None:
                dpg.configure_item(SOURCE_CODE_TAG, default_value=source_code)
                if self.debugger is not None:
                    self.debugger.enable_build_only()
        else:
            if self.debugger is not None:
                self.debugger.disable_all()
            dpg.configure_item(SOURCE_CODE_TAG, default_value='There are uninitialized nodes in the\nflowchart.')

    def draw_add_button(self, node: Node) -> bool:
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

    def resize(self) -> None:
        '''Sets the size of the drawing area.'''
        width, height = self.parent_size
        width += 14
        for node in self.selected_flowchart:
            (_, _, max_x, max_y) = node.bounds
            if max_x > width:
                width = max_x
            if max_y > height:
                height = max_y
        dpg.set_item_height(FLOWCHART_TAG, height)
        dpg.set_item_width(FLOWCHART_TAG, width)

    def get_point_on_canvas(self, point_on_screen: tuple[int, int]) -> tuple[int, int]:
        '''Maps the point in screen coordinates to canvas coordinates.'''
        offsetX, offsetY = dpg.get_item_rect_min(FLOWCHART_TAG)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
