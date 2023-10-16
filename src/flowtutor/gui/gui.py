from __future__ import annotations
from re import search
from typing import TYPE_CHECKING, Any, Optional, Type, Union, cast
from os.path import join, dirname
from shapely.geometry import Point
from blinker import signal
from dependency_injector.wiring import Provide, inject
from itertools import repeat, chain
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.template import Template
from flowtutor.gui.menubar_main import MenubarMain
from flowtutor.gui.section_node_extras import SectionNodeExtras
from flowtutor.gui.sidebar import Sidebar
from flowtutor.gui.sidebar_functionend import SidebarFunctionEnd
from flowtutor.gui.sidebar_multi import SidebarMulti
from flowtutor.gui.sidebar_none import SidebarNone
from flowtutor.gui.sidebar_template import SidebarTemplate
from flowtutor.gui.window_types import WindowTypes
from flowtutor.codegenerator import CodeGenerator
from flowtutor.gui.debugger import Debugger
from flowtutor.gui.sidebar_functionstart import SidebarFunctionStart


if TYPE_CHECKING:
    from flowtutor.language_service import LanguageService
    from flowtutor.util_service import UtilService
    from flowtutor.modal_service import ModalService
    from flowtutor.settings_service import SettingsService
    from flowtutor.flowchart.node import Node

FLOWCHART_TAG = 'flowchart'
ADD_BUTTON_TAG = 'add_button'


class GUI:
    '''The top level GUI container.'''

    hovered_add_button: Optional[str] = None
    '''The tag of the add button in the flowchart, that the mouse is hovering over.'''

    selected_nodes: list[Node] = []
    '''A list of nodes currently selected in the flowchart.'''

    drag_offsets: list[tuple[int, int]] = []
    '''The offset of the currently dragging node to its origin before moving'''

    is_mouse_dragging: bool = False
    '''True if the user is holding the mouse button down and dragging it.'''

    is_selecting: bool = False
    '''True if the user is selecting with a selection fence.'''

    drag_origin: tuple[int, int] = (0, 0)
    '''The mouse position where a dragging move has originated.'''

    parent_size: tuple[int, int] = (0, 0)
    '''The size of the GUI parent'''

    mouse_position: Optional[tuple[int, int]] = None
    '''The last registered position of the mouse relative to the window.'''

    mouse_position_on_canvas: Optional[tuple[int, int]] = None
    '''The last registered mouse position relative to the canvas.'''

    prev_source_code = ''
    '''The last generated source code.'''

    debugger: Optional[Debugger] = None
    '''The debugger GUI instance.'''

    variable_table_id: Optional[int] = None
    '''The dpg tag of the local variable table.'''

    selected_flowchart_name: str = 'main'
    '''The name of the currently selected flowchart'''

    sidebar_title_tag: Optional[str | int] = None
    '''The dpg tag of the sidebar title.'''

    file_path: Optional[str] = None
    '''The path of the current FlowTutor project file.'''

    selection_rect: Union[int, str] = 0
    '''The tag of the dpg rectangle item, representing the selection fence.'''

    @property
    def selected_node(self) -> Optional[Node]:
        '''The first of the currently selected nodes.'''
        return self.selected_nodes[0] if self.selected_nodes else None

    @property
    def selected_flowchart(self) -> Flowchart:
        '''The currently selected flowchart.'''
        return self.flowcharts[self.selected_flowchart_name]

    @inject
    def __init__(self,
                 width: int,
                 height: int,
                 utils_service: UtilService = Provide['utils_service'],
                 code_generator: CodeGenerator = Provide['code_generator'],
                 modal_service: ModalService = Provide['modal_service'],
                 settings_service: SettingsService = Provide['settings_service'],
                 language_service: LanguageService = Provide['language_service']):
        self.width = width
        self.height = height
        self.code_generator = code_generator
        self.modal_service = modal_service
        self.settings_service = settings_service
        self.language_service = language_service
        self.utils_service = utils_service

        # Start with an empty main function flowchart object.
        self.flowcharts = {
            'main': Flowchart('main', {})
        }

        signal('hit-line').connect(self.on_hit_line)
        signal('program-finished').connect(self.on_program_finished)
        signal('variables').connect(self.on_variables)

        dpg.create_context()

        # Load image assets.
        for image in ['c', 'python', 'run', 'stop', 'step_into', 'step_over', 'hammer', 'trash', 'pencil']:
            image_path = join(dirname(__file__), f'assets/{image}.png')
            image_width, image_height, _, image_data = dpg.load_image(image_path)
            with dpg.texture_registry():
                dpg.add_static_texture(width=image_width, height=image_height,
                                       default_value=image_data, tag=f'{image}_image')

        # Load typeface assets.
        with dpg.font_registry():
            default_font = dpg.add_font(join(dirname(__file__), 'assets/inconsolata.ttf'), 18)
            dpg.add_font(join(dirname(__file__),
                         'assets/inconsolata.ttf'), 22, tag='header_font')
        dpg.bind_font(default_font)

        # Register keyboard handlers, for shortcuts
        with dpg.handler_registry():
            if self.utils_service.is_mac_os:
                dpg.add_key_press_handler(dpg.mvKey_LWin, callback=self.on_ctrl_key)
                dpg.add_key_press_handler(dpg.mvKey_RWin, callback=self.on_ctrl_key)
            else:
                dpg.add_key_press_handler(dpg.mvKey_Control, callback=self.on_ctrl_key)

        # Insert main menubar GUI
        self.menubar_main = MenubarMain(self)

        # Create main window, including menu options and sidebars.
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

                    # Insert side bar GUIs for different node types.
                    self.sidebar_none = SidebarNone(self)
                    self.sidebar_function_start = SidebarFunctionStart(self)
                    self.sidebar_function_end = SidebarFunctionEnd(self)
                    self.sidebar_template = SidebarTemplate(self)
                    self.sidebar_multi = SidebarMulti(self)

                    self.sidebars: dict[Union[Type[Node], Type[list[Any]], Type[None]], Sidebar] = {
                        type(None): self.sidebar_none,
                        FunctionStart: self.sidebar_function_start,
                        FunctionEnd: self.sidebar_function_end,
                        Template: self.sidebar_template,
                        list: self.sidebar_multi
                    }

                    # Insert types window GUI.
                    self.window_types = WindowTypes(self)

                    # Insert node extras section GUI.
                    self.section_node_extras = SectionNodeExtras(self)

        # Register window resize handler.
        with dpg.item_handler_registry() as window_handler:
            dpg.add_item_resize_handler(callback=self.on_window_resize)
        dpg.bind_item_handler_registry(self.main_window, window_handler)

        dpg.configure_app()

        # Load window size from the last time FlowTutor was executed.
        self.parent_size = (int(self.settings_service.get_setting('width', '1000') or 1000),
                            int(self.settings_service.get_setting('height', '1000') or 1000))

        dpg.create_viewport(title='FlowTutor', width=self.parent_size[0], height=self.parent_size[1])

        # Load used theme from the last time FlowTutor was executed.
        if self.settings_service.get_setting('theme', 'light') == 'light':
            dpg.bind_theme(self.utils_service.get_theme_light())
        else:
            dpg.bind_theme(self.utils_service.get_theme_dark())

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        # Create main drawing area and source code text area.
        with dpg.child_window(parent=self.main_group,
                              border=False,
                              height=-1,
                              width=-1,
                              no_scrollbar=True,
                              no_scroll_with_mouse=True):
            with dpg.child_window(border=False, height=-255, no_scrollbar=True, no_scroll_with_mouse=True):
                with dpg.item_handler_registry() as window_handler:
                    dpg.add_item_resize_handler(callback=self.on_window_resize)
                with dpg.table(header_row=False, resizable=True):
                    dpg.add_table_column(init_width_or_weight=2)
                    dpg.add_table_column(init_width_or_weight=1)

                    with dpg.table_row():
                        with dpg.table_cell():
                            with dpg.tab_bar(
                                    reorderable=True,
                                    callback=self.on_selected_tab_changed) as self.function_tab_bar:
                                self.refresh_function_tabs()
                            with dpg.child_window(horizontal_scrollbar=True) as self.flowchart_container:
                                # Remove the padding of the flowchart container.
                                with dpg.theme() as item_theme:
                                    with dpg.theme_component(dpg.mvChildWindow):
                                        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,
                                                            0.0,
                                                            category=dpg.mvThemeCat_Core)
                                dpg.bind_item_theme(self.flowchart_container, item_theme)

                                # Insert main drawing area.
                                dpg.add_drawlist(tag=FLOWCHART_TAG,
                                                 width=self.width,
                                                 height=self.height)

                                # Register mouse events.
                                with dpg.handler_registry():
                                    dpg.add_mouse_move_handler(callback=self.on_hover)
                                    dpg.add_mouse_drag_handler(callback=self.on_drag)
                                    dpg.add_mouse_click_handler(callback=self.on_mouse_click)
                                    dpg.add_mouse_release_handler(callback=self.on_mouse_release)
                                    dpg.add_key_press_handler(
                                        dpg.mvKey_Delete, callback=self.on_delete_press)
                        with dpg.table_cell():
                            # Insert source code text area.
                            self.source_code_input = dpg.add_input_text(multiline=True,
                                                                        height=-1,
                                                                        width=-1,
                                                                        readonly=True)
                            dpg.bind_item_handler_registry(self.source_code_input, window_handler)

            # Create debugger section.
            with dpg.group(horizontal=True):
                with dpg.child_window(width=-410, border=False, height=250) as debugger_window:
                    # Insert debugger GUI.
                    self.debugger = Debugger(debugger_window)
                with dpg.child_window(width=400, border=False, height=250):
                    dpg.add_spacer(height=30)
                    dpg.add_text('Variables')
                    # Insert local variables table.
                    with dpg.table(header_row=True, row_background=True,
                                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                   borders_outerV=True, delay_search=True) as table_id:
                        self.variable_table_id = table_id
                        dpg.add_table_column(label='Name')
                        dpg.add_table_column(label='Value')

    def refresh_function_tabs(self) -> None:
        '''Delete all function tabs and reinsert the from the list of flowcharts.'''
        for tab in dpg.get_item_children(self.function_tab_bar)[1]:
            dpg.delete_item(tab)
        for func in self.flowcharts.keys():
            dpg.add_tab(label=func, user_data=func, parent=self.function_tab_bar)
        dpg.add_tab_button(label='+', callback=self.menubar_main.on_add_function, parent=self.function_tab_bar)

    def on_ctrl_key(self) -> None:
        '''Handle Ctrl-shortcuts'''
        if not self.language_service.is_initialized:
            return
        if dpg.is_key_down(dpg.mvKey_A):
            for node in self.selected_flowchart:
                self.selected_nodes.append(node)
                self.redraw_all(True)
        elif dpg.is_key_down(dpg.mvKey_S):
            self.menubar_main.on_save()

    def on_selected_tab_changed(self, _: Any, tab: Union[int, str]) -> None:
        '''Handle changes of the selected function tab.

        Parameters:
            tab (Union[int, str]): The dpg tag of the tab.
        '''
        self.clear_flowchart()
        self.selected_flowchart_name = dpg.get_item_user_data(tab)
        self.clear_selected_nodes()
        self.on_select_node(self.selected_flowchart.root)
        self.redraw_all(True)

    def on_hit_line(self, _: Any, **kw: int) -> None:
        '''Handle line hits from the debugger.

        Switches to the corresponding function tab and moves the debug cursor.
        '''
        line = kw['line']
        if self.debugger:
            self.debugger.enable_all()
        node_hit = False
        for func in self.flowcharts.values():
            for node in func:
                node.has_debug_cursor = line in node.lines
                node_hit = node_hit or node.has_debug_cursor
                # Switches to the flowcharts, where the break point is hit.
                if node.has_debug_cursor:
                    for tab in dpg.get_item_children(self.function_tab_bar)[1]:
                        if dpg.get_item_user_data(tab) == func.root.name:
                            dpg.set_value(self.function_tab_bar, tab)

        # If the hit line is not part of any node, then make another step.
        if not node_hit and self.debugger:
            self.debugger.on_debug_step_over()
        self.redraw_all(True)

    def on_variables(self, _: Any, **kw: dict[str, str]) -> None:
        '''Handle recieving varaible assignments from the debugger.

        Clears the local variable table and reinserts the new assignments.
        '''
        variables = kw['variables']
        if self.debugger:
            for row_id in dpg.get_item_children(self.variable_table_id)[1]:
                dpg.delete_item(row_id)
            if len(variables) > 0:
                for variable in variables:
                    with dpg.table_row(parent=self.variable_table_id):
                        dpg.add_text(variable)
                        dpg.add_text(variables[variable])
        self.redraw_all(True)

    def on_program_finished(self, _: Any, **kw: dict[str, str]) -> None:
        '''Handle the program finishing/

        Resets the debugger buttons, the debug cursor and the local variable table.
        '''
        for flowchart in self.flowcharts.values():
            for node in flowchart:
                node.has_debug_cursor = False
        if self.debugger:
            self.debugger.enable_build_and_run()
        for row_id in dpg.get_item_children(self.variable_table_id)[1]:
            dpg.delete_item(row_id)
        self.redraw_all(True)

    def on_select_node(self, node: Optional[Node]) -> None:
        '''Handles the user selecting a node with the mouse.'''

        if node in self.selected_nodes:
            return

        if node:
            node.needs_refresh = True
            self.selected_nodes.append(node)
        else:
            self.clear_selected_nodes()

        # Hides a sidebars
        [s.hide() for s in self.sidebars.values()]

        dpg.hide_item('function_management_group')

        # SHows the correct sidebars.
        if len(self.selected_nodes) > 1:
            self.section_node_extras.hide()
            self.sidebar_multi.show(node)
        else:
            self.section_node_extras.toggle(node)
            sidebar = self.sidebars.get(type(node))
            if sidebar:
                sidebar.show(node)

        # Redraws all nodes, if the need it.
        self.redraw_all()

    def on_window_resize(self) -> None:
        '''Handles the window resizing event.'''
        (width, height) = dpg.get_item_rect_size(self.flowchart_container)
        self.parent_size = (width, height)
        self.resize()
        self.settings_service.set_setting('height', dpg.get_viewport_height())
        self.settings_service.set_setting('width', dpg.get_viewport_width())

    def on_hover(self, _: Any, data: tuple[int, int]) -> None:
        '''Handles the mouse hovering over the window.

        Sets the mouse poition variable and redraws all objects.
        '''
        if not self.language_service.is_initialized:
            return
        self.mouse_position = data
        if not dpg.is_item_hovered(FLOWCHART_TAG):
            self.mouse_position_on_canvas = None
            return
        self.mouse_position_on_canvas = self.get_point_on_canvas(data)
        for node in self.selected_flowchart:
            # If the hover state of the node changes, it needs to be refreshed.
            is_hovered_before = node.is_hovered
            node.is_hovered = node.shape.contains(Point(*self.mouse_position_on_canvas))
            node.needs_refresh = is_hovered_before != node.is_hovered
            if node.needs_refresh:
                node.redraw(self.selected_flowchart, self.selected_nodes,
                            self.utils_service.theme_colors[dpg.mvThemeCol_Text])
        self.redraw_all()

    def on_drag(self) -> None:
        '''Handles mouse dragging on the current window.

        Redraws the currently dragging node to its new position.
        If no node is selected, the selection fence gets drawn.
        '''
        if not self.language_service.is_initialized or\
                not self.mouse_position_on_canvas or not self.is_mouse_dragging:
            return

        if self.is_selecting:
            # Draws the selection fence.
            if self.selection_rect and dpg.does_item_exist(self.selection_rect):
                dpg.configure_item(self.selection_rect, show=True, pmin=self.drag_origin,
                                   pmax=self.mouse_position_on_canvas)
            else:
                self.selection_rect = dpg.draw_rectangle(self.drag_origin,
                                                         self.mouse_position_on_canvas,
                                                         parent=FLOWCHART_TAG,
                                                         fill=(66, 150, 250, 51),
                                                         color=(66, 150, 250, 128))
            # Finds nodes in the selection fence.
            nodes_in_selection = self.selected_flowchart.find_nodes_in_selection(
                self.drag_origin,
                self.mouse_position_on_canvas)
            self.clear_selected_nodes()
            if nodes_in_selection:
                # Selectes nodes inside fence.
                for selected_node in nodes_in_selection:
                    self.on_select_node(selected_node)
        elif self.selected_nodes:
            # Moves selected nodes.
            (cX, cY) = self.mouse_position_on_canvas
            for selected_node, drag_offset in zip(self.selected_nodes, self.drag_offsets):
                (oX, oY) = drag_offset
                parents = self.selected_flowchart.find_parents(selected_node)
                for parent in parents:
                    parent.needs_refresh = True
                selected_node._needs_refresh = True
                selected_node.pos = (cX - oX, cY - oY)
        self.redraw_all()

    def on_mouse_click(self) -> None:
        '''Handles pressing down of the mouse button.'''
        if not self.language_service.is_initialized or not self.mouse_position_on_canvas:
            return

        hovered_node = self.selected_flowchart.find_hovered_node(self.mouse_position_on_canvas)

        # Sets the drag origin, in case the user drags the hovered node.
        self.drag_origin = self.mouse_position_on_canvas

        if hovered_node not in self.selected_nodes and not self.utils_service.is_multi_modifier_down():
            self.clear_selected_nodes()

        self.on_select_node(hovered_node)
        if not hovered_node:
            self.is_selecting = True

        if self.hovered_add_button:
            # If themouse is over an add button, then the dialog for a new node is openend.
            m = search(r'(.*)\[(.*)\]', self.hovered_add_button)
            if m:
                parent_tag = m.group(1)
                src_index = m.group(2)
                parent = self.selected_flowchart.find_node(parent_tag)

            def callback(node: Node) -> None:
                if parent:
                    self.selected_flowchart.add_node(parent, node, int(src_index))
                    self.mouse_position_on_canvas = None
                    self.redraw_all()
                    self.resize()
            self.modal_service.show_node_type_modal(self.selected_flowchart, callback, self.mouse_position or (0, 0))
        elif self.selected_nodes:
            # If nodes are already selected, dragging starts.
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
        '''Handles the realeas of the mouse button.'''
        if dpg.does_item_exist(self.selection_rect):
            dpg.configure_item(self.selection_rect, show=False)
        self.is_mouse_dragging = False
        self.is_selecting = False
        self.resize()

    def on_delete_press(self) -> None:
        '''Handle if the delete button or the delete key is pressed.'''
        if not self.selected_node:
            return

        def callback() -> None:
            if self.selected_nodes:
                self.selected_flowchart.clear()
                for selected_node in self.selected_nodes:
                    self.selected_flowchart.remove_node(selected_node)
                self.on_select_node(None)
                self.redraw_all(True)
                self.resize()
        callback()

    def set_sidebar_title(self, title: str) -> None:
        '''Sets the title of the sidebar GUI.

        Parameters:
            title (str): New title.'''
        dpg.configure_item(self.sidebar_title_tag, default_value=title)

    def clear_flowchart(self, select_lang: bool = False) -> None:
        '''Clears the current program to start fresh.

        Parameters:
            select_lang (bool): Shows the language selection if true.
        '''
        self.on_select_node(None)
        self.is_mouse_dragging = False
        for item in dpg.get_item_children(FLOWCHART_TAG)[2]:
            dpg.delete_item(item)
        if select_lang:
            self.language_service.is_initialized = False
            self.modal_service.show_welcome_modal(self)

    def clear_selected_nodes(self) -> None:
        '''Empties the list of selected nodes.'''
        for selected_node in self.selected_nodes:
            selected_node.needs_refresh = True
        self.selected_nodes.clear()

    def get_ordered_flowcharts(self) -> list[Flowchart]:
        '''Get a ordered list of flowcharts, by sorting the tabs by their x-position on screen.
           (workaround for missing feature in dearpygui)
        '''
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

    def redraw_all(self, force: bool = False) -> None:
        '''Redraws all nodes, if they need refresh.

        Parameters:
            force (bool): If this is set to true, all nodes get redrawn, regardless of their needs_refresh state.
        '''
        if not self.language_service.is_initialized:
            return
        self.hovered_add_button = None

        for node in [n for n in self.selected_flowchart if force or n.needs_refresh]:
            node.needs_refresh = False
            node.redraw(self.selected_flowchart, self.selected_nodes,
                        self.utils_service.theme_colors[dpg.mvThemeCol_Text])

        self.redraw_add_button()
        if self.selected_flowchart.is_initialized():
            # If the flowchart is fully initialized, generate the corresponding source code.
            source_code = self.code_generator.write_source_file(self.get_ordered_flowcharts())
            if source_code:
                dpg.configure_item(self.source_code_input, default_value=source_code)
                if self.debugger:
                    self.debugger.enable_build_only(self.selected_flowchart)
        else:
            if self.debugger:
                self.debugger.disable_all()
            dpg.configure_item(self.source_code_input, default_value='There are uninitialized nodes in the\nflowchart.')

    def redraw_add_button(self) -> None:
        '''Draws a Symbol for adding connected nodes, if the mouse is over a connection point.'''

        if not self.language_service.is_initialized or not self.mouse_position_on_canvas:
            if dpg.does_item_exist(ADD_BUTTON_TAG):
                dpg.delete_item(ADD_BUTTON_TAG)
            return

        all_out_points = list(chain.from_iterable([zip(n.out_points, repeat(n)) for n in self.selected_flowchart]))

        close_point, close_node = next(filter(lambda t: Point(t[0]).distance(
            Point(self.mouse_position_on_canvas)) < 12, all_out_points), (None, None))

        if dpg.does_item_exist(ADD_BUTTON_TAG):
            dpg.delete_item(ADD_BUTTON_TAG)

        if close_point and close_node:
            with dpg.draw_node(tag=ADD_BUTTON_TAG, parent=FLOWCHART_TAG):
                dpg.draw_circle(close_point, 12, fill=(255, 255, 255))
                dpg.draw_circle(close_point, 12, color=(0, 0, 0))
                x, y = close_point
                dpg.draw_text((x - 5.5, y - 12), '+',
                              color=(0, 0, 0), size=24)
                src_ind = close_node.out_points.index(close_point)
                self.hovered_add_button = f'{close_node.tag}[{src_ind}]'

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
        '''Maps the point in screen coordinates to canvas coordinates.

        Parameters:
            point_on_screen (tuple[int, int]): The coordinates of the point relative to the window.
        '''
        offsetX, offsetY = dpg.get_item_rect_min(FLOWCHART_TAG)
        x, y = point_on_screen
        return (x - offsetX, y - offsetY)
