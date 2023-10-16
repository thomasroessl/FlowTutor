from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from pickle import dump
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.flowchart import Flowchart

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI
    from flowtutor.language_service import LanguageService
    from flowtutor.settings_service import SettingsService
    from flowtutor.modal_service import ModalService
    from flowtutor.util_service import UtilService


class MenubarMain:
    '''The main menu bar placed at the top of the window.'''

    @inject
    def __init__(self,
                 gui: GUI,
                 settings_service: SettingsService = Provide['settings_service'],
                 language_service: LanguageService = Provide['language_service'],
                 modal_service: ModalService = Provide['modal_service'],
                 utils_service: UtilService = Provide['utils_service']) -> None:
        self.gui = gui
        self.settings_service = settings_service
        self.language_service = language_service
        self.modal_service = modal_service
        self.utils_service = utils_service
        with dpg.viewport_menu_bar(tag='menu_bar'):
            with dpg.menu(label='File'):
                dpg.add_menu_item(label='New Program', callback=self.on_new)
                dpg.add_separator()
                dpg.add_menu_item(label='Open...', callback=lambda: self.modal_service.show_open_dialog(self.gui))
                dpg.add_separator()
                dpg.add_menu_item(label='Save', callback=self.on_save, shortcut='S')
                dpg.add_menu_item(label='Save As...', callback=lambda: self.modal_service.show_save_as_dialog(self.gui))
            with dpg.menu(label='Edit'):
                dpg.add_menu_item(label='Add Function', callback=self.on_add_function)
                dpg.add_separator()
                dpg.add_menu_item(label='Clear Current Function', callback=self.on_clear)

            with dpg.menu(label='View'):
                with dpg.menu(label='Theme'):
                    dpg.add_menu_item(label='Light', callback=self.on_light_theme_menu_item_click)
                    dpg.add_menu_item(label='Dark', callback=self.on_dark_theme_menu_item_click)
            with dpg.menu(label='Help'):
                dpg.add_menu_item(label='Paths', callback=self.modal_service.show_paths_window)

    def on_new(self) -> None:
        '''Handles pressing of the 'New' menu item.'''
        def callback() -> None:
            self.gui.file_path = None
            dpg.set_viewport_title('FlowTutor')
            self.gui.clear_flowchart(True)
            self.gui.flowcharts = {
                'main': Flowchart('main', {})
            }
            self.gui.redraw_all(True)
            self.gui.refresh_function_tabs()
        self.modal_service.show_approval_modal(
            'New Program', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    def on_clear(self) -> None:
        '''Handles pressing of the 'Clear' menu item.'''
        def callback() -> None:
            self.gui.selected_flowchart.reset()
            self.gui.clear_flowchart(True)
            self.gui.redraw_all(True)
        self.modal_service.show_approval_modal(
            'Clear', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    def on_save(self) -> None:
        '''Handles pressing of the 'Save' menu item.'''
        if self.gui.file_path:
            with open(self.gui.file_path, 'wb') as file:
                dump(self.gui.flowcharts, file)
        else:
            self.modal_service.show_save_as_dialog(self.gui)

    def on_light_theme_menu_item_click(self) -> None:
        '''Handles pressing of the 'Light theme' menu item.'''
        dpg.bind_theme(self.utils_service.get_theme_light())
        self.gui.redraw_all(True)
        self.gui.settings_service.set_setting('theme', 'light')

    def on_dark_theme_menu_item_click(self) -> None:
        '''Handles pressing of the 'Dark theme' menu item.'''
        dpg.bind_theme(self.utils_service.get_theme_dark())
        self.gui.redraw_all(True)
        self.gui.settings_service.set_setting('theme', 'dark')

    def on_add_function(self) -> None:
        '''Handles pressing of the 'Add Function' menu item.'''
        def callback(name: str) -> None:
            self.gui.flowcharts[name] = Flowchart(name, self.gui.selected_flowchart.lang_data)
            self.gui.refresh_function_tabs()
        i = len(self.gui.flowcharts.values())
        new_name = f'fun_{i}'
        while new_name in self.gui.flowcharts.keys():
            i += 1
            new_name = f'fun_{i}'
        self.modal_service.show_input_text_modal(
            'New Function',
            'Name',
            new_name,
            callback)
