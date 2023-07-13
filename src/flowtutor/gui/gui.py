from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Type, Union, cast
import re
import os.path
import dearpygui.dearpygui as dpg
from shapely.geometry import Point
from blinker import signal
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
from flowtutor.flowchart.template import Template
from flowtutor.gui.menubar_main import MenubarMain
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
from flowtutor.gui.sidebar_multi import SidebarMulti
from flowtutor.gui.sidebar_none import SidebarNone
from flowtutor.gui.sidebar_whileloop import SidebarWhileLoop
from flowtutor.gui.sidebar_output import SidebarOutput
from flowtutor.gui.sidebar_snippet import SidebarSnippet
from flowtutor.gui.sidebar_template import SidebarTemplate
from flowtutor.gui.window_types import WindowTypes
from flowtutor.modal_service import ModalService
from flowtutor.settings_service import SettingsService
from flowtutor.codegenerator import CodeGenerator
from flowtutor.gui.debugger import Debugger
from flowtutor.gui.sidebar_functionstart import SidebarFunctionStart
from flowtutor.gui.themes import create_theme_dark, create_theme_light
from flowtutor.util_service import UtilService


if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'


class GUI:

    hovered_add_button: Optional[str] = None

    selected_nodes: list[Node] = []

    # The offset of the currently dragging node to its origin before moving
    drag_offsets: list[tuple[int, int]] = []

    is_mouse_dragging: bool = False

    is_selecting: bool = False

    drag_origin: tuple[int, int] = (0, 0)

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

    selection_rect: Union[int, str] = 0

    @property
    def selected_node(self) -> Optional[Node]:
        return self.selected_nodes[0] if self.selected_nodes else None

    @property
    def selected_flowchart(self) -> Flowchart:
        return self.flowcharts[self.selected_flowchart_name]

    @inject
    def __init__(self,
                 width: int,
                 height: int,
                 utils_service: UtilService = Provide['utils_service'],
                 code_generator: CodeGenerator = Provide['code_generator'],
                 modal_service: ModalService = Provide['modal_service'],
                 settings_service: SettingsService = Provide['settings_service']):
        self.width = width
        self.height = height
        self.code_generator = code_generator
        self.modal_service = modal_service
        self.settings_service = settings_service
        self.utils_service = utils_service
        self.flowcharts = {
            'main': Flowchart('main')
        }

        signal('hit-line').connect(self.on_hit_line)
        signal('program-finished').connect(self.on_program_finished)
        signal('variables').connect(self.on_variables)

        dpg.create_context()

        for image in ['c', 'run', 'stop', 'step_into', 'step_over', 'hammer', 'trash', 'pencil']:
            image_path = os.path.join(os.path.dirname(__file__), f'assets/{image}.png')
            image_width, image_height, _, image_data = dpg.load_image(image_path)
            with dpg.texture_registry():
                dpg.add_static_texture(width=image_width, height=image_height,
                                       default_value=image_data, tag=f'{image}_image')

        with dpg.font_registry():
            default_font = dpg.add_font(os.path.join(os.path.dirname(__file__), 'assets/inconsolata.ttf'), 18)
            dpg.add_font(os.path.join(os.path.dirname(__file__),
                         'assets/inconsolata.ttf'), 22, tag='header_font')
        dpg.bind_font(default_font)

        self.menubar_main = MenubarMain(self)

        with dpg.window() as self.main_window:
            with dpg.group(horizontal=True) as self.main_group:
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
                    self.sidebar_template = SidebarTemplate(self)
                    self.sidebar_multi = SidebarMulti(self)

                    self.sidebars: dict[Union[Type[Node], Type[list[Any]], Type[None]], Sidebar] = {
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
                        Snippet: self.sidebar_snippet,
                        Template: self.sidebar_template,
                        list: self.sidebar_multi
                    }

                    self.window_types = WindowTypes(self)

                    self.section_node_extras = SectionNodeExtras(self)

        with dpg.item_handler_registry() as window_handler:
            dpg.add_item_resize_handler(callback=self.on_window_resize)
        dpg.bind_item_handler_registry(self.main_window, window_handler)

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
        dpg.set_primary_window(self.main_window, True)

        with dpg.child_window(parent=self.main_group, border=False, width=-1):
            with dpg.child_window(border=False, height=-254):
                with dpg.group(horizontal=True):
                    with dpg.group(width=-410):
                        with dpg.tab_bar(
                                reorderable=True,
                                callback=self.on_selected_tab_changed) as self.function_tab_bar:
                            self.refresh_function_tabs()
                        with dpg.child_window(horizontal_scrollbar=True) as self.flowchart_container:

                            # Remove the padding of the flowchart container
                            with dpg.theme() as item_theme:
                                with dpg.theme_component(dpg.mvChildWindow):
                                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0.0, category=dpg.mvThemeCat_Core)
                            dpg.bind_item_theme(self.flowchart_container, item_theme)

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
                    with dpg.group(width=400):
                        self.source_code_input = dpg.add_input_text(multiline=True, height=-1, readonly=True)
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
        for tab in dpg.get_item_children(self.function_tab_bar)[1]:
            dpg.delete_item(tab)
        for func in self.flowcharts.keys():
            dpg.add_tab(label=func, user_data=func, parent=self.function_tab_bar)
        dpg.add_tab_button(label='+', callback=self.menubar_main.on_add_function, parent=self.function_tab_bar)

    def on_selected_tab_changed(self, _: Any, tab: Union[int, str]) -> None:
        self.clear_flowchart()
        self.selected_flowchart_name = dpg.get_item_user_data(tab)
        self.selected_nodes.clear()
        self.on_select_node(self.selected_flowchart.root)
        self.redraw_all()

    def on_hit_line(self, _: Any, **kw: int) -> None:
        line = kw['line']
        if self.debugger:
            self.debugger.enable_all()
        for func in self.flowcharts.values():
            for node in func:
                node.has_debug_cursor = line in node.lines
                # Switches to the flowcharts, where the break point is hit
                if node.has_debug_cursor:
                    for tab in dpg.get_item_children(self.function_tab_bar)[1]:
                        if dpg.get_item_user_data(tab) == func.root.name:
                            dpg.set_value(self.function_tab_bar, tab)
        self.redraw_all()

    def on_variables(self, _: Any, **kw: dict[str, str]) -> None:
        variables = kw['variables']
        if self.debugger:
            for row_id in dpg.get_item_children(self.variable_table_id)[1]:
                dpg.delete_item(row_id)
            if len(variables) > 0:
                for variable in variables:
                    with dpg.table_row(parent=self.variable_table_id):
                        dpg.add_text(variable)
                        dpg.add_text(variables[variable])
        self.redraw_all()

    def on_program_finished(self, _: Any, **kw: dict[str, str]) -> None:
        for flowchart in self.flowcharts.values():
            for node in flowchart:
                node.has_debug_cursor = False
        if self.debugger:
            self.debugger.enable_build_and_run()
        self.redraw_all()

    def on_select_node(self, node: Optional[Node]) -> None:

        if node in self.selected_nodes:
            return

        self.selected_nodes.append(node) if node else self.selected_nodes.clear()

        [s.hide() for s in self.sidebars.values()]

        dpg.hide_item('function_management_group')

        if len(self.selected_nodes) > 1:
            self.section_node_extras.hide()
            self.sidebar_multi.show(node)
        else:
            self.section_node_extras.toggle(node)
            sidebar = self.sidebars.get(type(node))
            if sidebar:
                sidebar.show(node)

    def on_window_resize(self) -> None:
        (width, height) = dpg.get_item_rect_size(self.flowchart_container)
        self.parent_size = (width, height)
        self.resize()
        self.settings_service.set_setting('height', dpg.get_viewport_height())
        self.settings_service.set_setting('width', dpg.get_viewport_width())

    def on_hover(self, _: Any, data: tuple[int, int]) -> None:
        '''Sets the mouse poition variable and redraws all objects.'''
        self.mouse_position = data
        if not dpg.is_item_hovered(FLOWCHART_TAG):
            self.mouse_position_on_canvas = None
            return
        self.mouse_position_on_canvas = self.get_point_on_canvas(data)
        self.redraw_all()

    def on_drag(self) -> None:
        '''Redraws the currently dragging node to its new position.'''
        if not self.mouse_position_on_canvas or not self.is_mouse_dragging:
            return

        if self.is_selecting:
            if self.selection_rect and dpg.does_item_exist(self.selection_rect):
                dpg.configure_item(self.selection_rect, show=True, pmin=self.drag_origin,
                                   pmax=self.mouse_position_on_canvas)
            else:
                self.selection_rect = dpg.draw_rectangle(self.drag_origin,
                                                         self.mouse_position_on_canvas,
                                                         parent=FLOWCHART_TAG,
                                                         fill=(66, 150, 250, 51),
                                                         color=(66, 150, 250, 128))
            nodes_in_selection = self.selected_flowchart.find_nodes_in_selection(
                self.drag_origin,
                self.mouse_position_on_canvas)
            self.selected_nodes.clear()
            if nodes_in_selection:
                for selected_node in nodes_in_selection:
                    self.on_select_node(selected_node)
        elif self.selected_nodes:
            (cX, cY) = self.mouse_position_on_canvas
            for selected_node, drag_offset in zip(self.selected_nodes, self.drag_offsets):
                (oX, oY) = drag_offset
                selected_node.pos = (cX - oX, cY - oY)

    def on_mouse_click(self) -> None:
        '''Handles pressing down of the mouse button.'''
        if not self.mouse_position_on_canvas:
            return
        hovered_node = self.selected_flowchart.find_hovered_node(self.mouse_position_on_canvas)
        self.drag_origin = self.mouse_position_on_canvas
        if hovered_node not in self.selected_nodes and not self.utils_service.is_multi_modifier_down():
            self.selected_nodes.clear()
        self.on_select_node(hovered_node)
        if not hovered_node:
            self.is_selecting = True
        if self.hovered_add_button:
            m = re.search(r'(.*)\[(.*)\]', self.hovered_add_button)
            if m:
                parent_tag = m.group(1)
                src_index = m.group(2)
                parent = self.selected_flowchart.find_node(parent_tag)

            def callback(node: Node) -> None:
                if parent:
                    self.selected_flowchart.add_node(parent, node, int(src_index))
                    self.redraw_all()
                    self.resize()
            self.modal_service.show_node_type_modal(callback, self.mouse_position or (0, 0))
        elif self.selected_nodes:
            self.is_mouse_dragging = True
            self.drag_offsets.clear()
            (cX, cY) = self.mouse_position_on_canvas
            for selected_node in self.selected_nodes:
                (pX, pY) = selected_node.pos
                self.drag_offsets.append((cX - pX, cY - pY))
        else:
            self.is_mouse_dragging = True
        self.redraw_all()

    def on_mouse_release(self) -> None:
        if dpg.does_item_exist(self.selection_rect):
            dpg.configure_item(self.selection_rect, show=False)
        self.is_mouse_dragging = False
        self.is_selecting = False
        self.resize()

    def on_delete_press(self) -> None:
        if not self.selected_node:
            return

        def callback() -> None:
            if self.selected_nodes:
                self.selected_flowchart.clear()
                for selected_node in self.selected_nodes:
                    self.selected_flowchart.remove_node(selected_node)
                self.on_select_node(None)
                self.redraw_all()
                self.resize()

        if any(map(lambda n: n.has_nested_nodes(), self.selected_nodes)):
            self.modal_service.show_approval_modal(
                'Delete Node(s)',
                'Nested nodes will also be deleted.',
                callback)
        else:
            callback()

    def set_sidebar_title(self, title: str) -> None:
        dpg.configure_item(self.sidebar_title_tag, default_value=title)

    def clear_flowchart(self) -> None:
        self.on_select_node(None)
        self.is_mouse_dragging = False
        for item in dpg.get_item_children(FLOWCHART_TAG)[2]:
            dpg.delete_item(item)

    def get_ordered_flowcharts(self) -> list[Flowchart]:
        '''Get a ordered list of flowcharts, by sorting the tabs by their x-position on screen.
           (workaround for missing feature in dearpygui)'''
        tabs = dpg.get_item_children(self.function_tab_bar)[1]
        filtered_tabs = list(filter(lambda tab: dpg.get_item_user_data(tab), tabs))
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
            node.redraw(self.selected_flowchart, self.mouse_position_on_canvas, self.selected_nodes)
            if not is_add_button_drawn and not self.is_selecting:
                is_add_button_drawn = self.draw_add_button(node)
        if self.selected_flowchart.is_initialized():
            source_code = self.code_generator.write_source_files(self.get_ordered_flowcharts())
            if source_code:
                dpg.configure_item(self.source_code_input, default_value=source_code)
                if self.debugger:
                    self.debugger.enable_build_only()
        else:
            if self.debugger:
                self.debugger.disable_all()
            dpg.configure_item(self.source_code_input, default_value='There are uninitialized nodes in the\nflowchart.')

    def draw_add_button(self, node: Node) -> bool:
        '''Draws a Symbol for adding connected nodes, if the mouse is over a connection point.
           Returns True if an add button was drawn.
        '''
        close_point = None
        if self.mouse_position_on_canvas:
            close_point = next(
                filter(
                    lambda p: Point(p).distance(Point(self.mouse_position_on_canvas)) < 12, node.out_points), None)
        if close_point:
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
                height = max_y + 100
        dpg.set_item_height(FLOWCHART_TAG, height)
        dpg.set_item_width(FLOWCHART_TAG, width)

    def get_point_on_canvas(self, point_on_screen: tuple[int, int]) -> tuple[int, int]:
        '''Maps the point in screen coordinates to canvas coordinates.'''
        offsetX, offsetY = dpg.get_item_rect_min(FLOWCHART_TAG)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
