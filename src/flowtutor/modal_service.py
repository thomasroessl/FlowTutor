from __future__ import annotations
from dependency_injector.wiring import Provide, inject
from os.path import basename, exists
from typing import TYPE_CHECKING, Any, Callable
from pickle import load, dump
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.template import Template

if TYPE_CHECKING:
    from flowtutor.language_service import LanguageService
    from flowtutor.settings_service import SettingsService
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.flowchart import Flowchart
    from flowtutor.flowchart.node import Node
    from flowtutor.gui.gui import GUI


class ModalService:
    '''A service to handle showing of modal dialogs.'''

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 settings_service: SettingsService = Provide['settings_service'],
                 language_service: LanguageService = Provide['language_service']):
        self.settings_service = settings_service
        self.language_service = language_service
        self.utils_service = utils_service

    def show_paths_window(self) -> None:
        '''Shows a Window with a table that shows some useful paths.

        - FlowTutor root
        - GCC executable
        - GDB executable
        - Templates
        - Working directory
        '''
        with dpg.window(
                label='FlowTutor',
                modal=True,
                tag='paths_window',
                width=600,
                height=-1,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('paths_window')):
            with dpg.table(
                    header_row=False,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True):
                dpg.add_table_column(width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_text('FlowTutor')
                    dpg.add_input_text(default_value=self.utils_service.get_root_dir(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('GCC executable')
                    dpg.add_input_text(default_value=self.utils_service.get_gcc_exe(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('GDB executable')
                    dpg.add_input_text(default_value=self.utils_service.get_gdb_exe(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('Templates')
                    dpg.add_input_text(default_value=self.utils_service.get_templates_path(''),
                                       width=-1,
                                       readonly=True)
                with dpg.table_row():
                    dpg.add_text('Working directory')
                    dpg.add_input_text(default_value=self.utils_service.get_temp_dir(), width=-1, readonly=True)

    def show_approval_modal(self, label: str, message: str, callback: Callable[[], None]) -> None:
        '''Shows a modal dialog asking for approval from the user.

        Parameters:
            label (str): The label of the window.
            message (str): The message to the user.
            callback (Callable[[], None]): The callback that gets executed upon approval.
        '''
        client_with = dpg.get_viewport_client_width()

        with dpg.window(
                label=label,
                modal=True,
                tag='approval_modal',
                autosize=True,
                width=500,
                pos=(client_with / 2 - 250, 30),
                no_open_over_existing_popup=False,
                no_close=True):
            dpg.add_text(message)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label='OK',
                    width=75,
                    callback=lambda: (dpg.delete_item('approval_modal'), callback()))
                dpg.add_button(
                    label='Cancel',
                    width=75,
                    callback=lambda: dpg.delete_item('approval_modal'))

    def show_welcome_modal(self, gui: GUI) -> None:
        '''Shows a modal dialog for creating a new project.

        Parameters:
            gui (GUI): A reference to the main gui object.
        '''
        client_with = dpg.get_viewport_client_width()

        if dpg.does_item_exist('welcome_modal'):
            dpg.show_item('welcome_modal')
            dpg.set_item_pos('welcome_modal', (client_with / 2 - 250, 40))
            return

        with dpg.window(
                label='Welcome',
                modal=True,
                tag='welcome_modal',
                width=500,
                no_title_bar=True,
                no_close=True,
                no_collapse=True,
                no_resize=True,
                no_open_over_existing_popup=False,
                pos=(client_with / 2 - 250, 30)):
            with dpg.theme() as lang_button_theme:
                with dpg.theme_component(dpg.mvImageButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255, 0), category=dpg.mvThemeCat_Core)

            with dpg.table(policy=dpg.mvTable_SizingFixedFit,
                           header_row=True,
                           borders_outerH=True,
                           borders_innerV=True,
                           borders_innerH=True,
                           borders_outerV=True):
                dpg.add_table_column(label='New', width_fixed=True, no_sort=True)
                dpg.add_table_column(label='Open', width_stretch=True, no_sort=True)
                with dpg.table_row():
                    with dpg.table_cell():
                        dpg.add_spacer(height=1)
                        for lang_id, data in self.language_service.get_languages().items():
                            if dpg.does_item_exist(f'{lang_id}_image'):
                                lang_button = dpg.add_image_button(
                                    f'{lang_id}_image',
                                    user_data=data,
                                    callback=lambda s: (self.on_select_language(gui, dpg.get_item_user_data(s)),
                                                        dpg.hide_item('welcome_modal')))
                                dpg.bind_item_theme(lang_button, lang_button_theme)
                            else:
                                dpg.add_button(
                                    label=data['name'],
                                    width=75,
                                    user_data=data,
                                    callback=lambda s: (self.on_select_language(gui, dpg.get_item_user_data(s)),
                                                        dpg.hide_item('welcome_modal')))
                    with dpg.table_cell():
                        dpg.add_spacer(height=1)
                        dpg.add_button(
                            label='Open...',
                            width=-1,
                            callback=lambda: self.show_open_dialog(gui))
                        dpg.add_text('Recents:')
                        recents = list(
                            filter(lambda r: exists(r), self.settings_service.get_setting('recents').split(',')))
                        self.settings_service.set_setting('recents', ','.join(recents))
                        for recent in filter(lambda r: r, recents):
                            dpg.add_button(
                                label=basename(recent),
                                width=-1,
                                user_data=recent,
                                callback=lambda s: (self.open_callback(gui, dpg.get_item_user_data(s)),
                                                    dpg.hide_item('welcome_modal')))

    def on_select_language(self, gui: GUI, lang_data: dict[str, Any]) -> None:
        '''Handles the event if a language is selected.'''
        gui.flowcharts['main'].lang_data = lang_data
        gui.language_service.finish_init(gui.flowcharts['main'])
        gui.sidebar_none.refresh()
        if gui.debugger:
            gui.debugger.refresh(gui.selected_flowchart)
        gui.redraw_all(True)

    def open_callback(self, gui: GUI, file_path: str) -> None:
        '''This method is called, when a project file is openend.

        Parameters:
            gui (GUI): A reference to the main gui object.
            file_path (str): The path to the project file to be openend.
        '''
        with open(file_path, 'rb') as file:
            gui.file_path = file_path
            dpg.set_viewport_title(f'FlowTutor - {file_path}')
            flowcharts: dict[str, Flowchart] = load(file)
            gui.flowcharts = flowcharts
            self.language_service.finish_init(gui.flowcharts['main'])
            gui.window_types.refresh()
            gui.sidebar_none.refresh()
            gui.redraw_all(True)
            gui.resize()
            gui.refresh_function_tabs()
            if gui.debugger:
                gui.debugger.enable_build_only(gui.flowcharts['main'])
            recents = set(self.settings_service.get_setting('recents').split(','))
            recents.add(file_path)
            self.settings_service.set_setting('recents', ','.join(recents))

    def show_save_as_dialog(self, gui: GUI) -> None:
        '''Shows a 'Save As' window for the current project.'''
        def callback(gui: GUI, file_path: str) -> None:
            with open(file_path, 'wb') as file:
                gui.file_path = file_path
                dpg.set_viewport_title(f'FlowTutor - {file_path}')
                dump(gui.flowcharts, file)
                recents = set(self.settings_service.get_setting('recents').split(','))
                recents.add(file_path)
                self.settings_service.set_setting('recents', ','.join(recents))
        if dpg.does_item_exist('save_as_dialog'):
            dpg.show_item('save_as_dialog')
            return
        with dpg.file_dialog(tag='save_as_dialog',
                             min_size=[500, 300],
                             directory_selector=False,
                             callback=lambda _, data: callback(gui, data['file_path_name'])):
            dpg.add_file_extension('.flowtutor', color=self.utils_service.theme_colors[dpg.mvThemeCol_Text])

    def show_open_dialog(self, gui: GUI) -> None:
        '''Shows a window for opening an existing project.'''
        if dpg.does_item_exist('open_dialog'):
            dpg.show_item('open_dialog')
            return
        with dpg.file_dialog(tag='open_dialog',
                             min_size=[500, 300],
                             directory_selector=False,
                             cancel_callback=lambda: self.show_welcome_modal(
                                 gui) if not self.language_service.is_initialized else None,
                             callback=lambda _, data: self.open_callback(gui, data['file_path_name'])):
            dpg.add_file_extension('.flowtutor', color=self.utils_service.theme_colors[dpg.mvThemeCol_Text])

    def show_input_text_modal(self,
                              label: str,
                              message: str,
                              default_value: str,
                              callback: Callable[[str], None]) -> None:
        '''Shows a modal dialog asking for approval from the user.

        Parameters:
            label (str): The label of the window.
            message (str): The message to the user.
            default_value (str): The suggested value in the input box.
            callback (Callable[[], None]): The callback that gets executed on OK.
        '''
        with dpg.window(
                label=label,
                modal=True,
                tag='input_text_modal',
                autosize=True,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('input_text_modal')):
            dpg.add_text(message)
            dpg.add_input_text(tag='input_text', default_value=default_value)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label='OK',
                    width=75,
                    callback=lambda: (callback(dpg.get_value('input_text')), dpg.delete_item('input_text_modal')))
                dpg.add_button(
                    label='Cancel',
                    width=75,
                    callback=lambda: dpg.delete_item('input_text_modal'))

    def show_node_type_modal(self,
                             flowchart: Flowchart,
                             callback: Callable[[Node], None],
                             pos: tuple[int, int]) -> None:
        '''Shows a window with a list of node types, that can be inserted.

        Parameters:
            flowchart (Flowchart): The flowchart the new node is to be added to.
            callback (Callable[[Node], None]): The callback that gets executed upon selection of a node type.
            pos (tuple[int, int]): The position of the window.
        '''
        with dpg.window(
                label='Add Node',
                pos=pos,
                modal=True,
                tag='node_type_modal',
                no_resize=True,
                autosize=True,
                on_close=lambda: dpg.delete_item('node_type_modal')):
            with dpg.group():
                for label, args in self.language_service.get_node_templates(flowchart).items():
                    dpg.add_button(
                        label=label,
                        width=200,
                        user_data=args,
                        callback=lambda s: (user_data := dpg.get_item_user_data(s),
                                            callback(Template(user_data)),
                                            dpg.delete_item('node_type_modal')))
