from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from pickle import dump, load

from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.gui.themes import create_theme_dark, create_theme_light

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class MenubarMain:

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.viewport_menu_bar(tag='menu_bar'):
            with dpg.menu(label='File'):
                dpg.add_menu_item(label='New Program', callback=self.on_new)
                dpg.add_separator()
                dpg.add_menu_item(label='Open...', callback=self.on_open)
                dpg.add_separator()
                dpg.add_menu_item(label='Save', callback=self.on_save)
                dpg.add_menu_item(label='Save As...', callback=self.on_save_as)
            with dpg.menu(label='Edit'):
                dpg.add_menu_item(label='Add Function', callback=self.on_add_function)
                dpg.add_separator()
                dpg.add_menu_item(label='Clear Current Function', callback=self.on_clear)

            with dpg.menu(label='View'):
                with dpg.menu(label='Theme'):
                    dpg.add_menu_item(label='Light', callback=self.on_light_theme_menu_item_click)
                    dpg.add_menu_item(label='Dark', callback=self.on_dark_theme_menu_item_click)
            with dpg.menu(label='Help'):
                dpg.add_menu_item(label='Paths', callback=self.gui.modal_service.show_paths_window)

    def on_new(self) -> None:
        def callback() -> None:
            self.gui.file_path = None
            dpg.set_viewport_title('FlowTutor')
            self.gui.clear_flowchart()
            self.gui.flowcharts = {
                'main': Flowchart('main')
            }
            self.gui.redraw_all()
            self.gui.refresh_function_tabs()
        self.gui.modal_service.show_approval_modal(
            'New Program', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    def on_open(self) -> None:
        def callback(file_path: str) -> None:
            with open(file_path, 'rb') as file:
                self.gui.file_path = file_path
                dpg.set_viewport_title(f'FlowTutor - {file_path}')
                self.gui.flowcharts = load(file)
                self.gui.window_types.refresh()
                self.gui.sidebar_none.refresh()
                self.gui.redraw_all()
                self.gui.refresh_function_tabs()
        self.gui.modal_service.show_open_modal(callback)

    def on_clear(self) -> None:
        def callback() -> None:
            self.gui.selected_flowchart.reset()
            self.gui.clear_flowchart()
            self.gui.redraw_all()
        self.gui.modal_service.show_approval_modal(
            'Clear', 'Are you sure? Any unsaved changes are going to be lost.', callback)

    def on_save(self) -> None:
        if self.gui.file_path:
            with open(self.gui.file_path, 'wb') as file:
                dump(self.gui.flowcharts, file)
        else:
            self.on_save_as()

    def on_save_as(self) -> None:
        def callback(file_path: str) -> None:
            with open(file_path, 'wb') as file:
                self.gui.file_path = file_path
                dpg.set_viewport_title(f'FlowTutor - {file_path}')
                dump(self.gui.flowcharts, file)
        self.gui.modal_service.show_save_as_modal(callback)

    def on_light_theme_menu_item_click(self) -> None:
        dpg.bind_theme(create_theme_light())
        self.gui.redraw_all()
        self.gui.settings_service.set_setting('theme', 'light')

    def on_dark_theme_menu_item_click(self) -> None:
        dpg.bind_theme(create_theme_dark())
        self.gui.redraw_all()
        self.gui.settings_service.set_setting('theme', 'dark')

    def on_add_function(self) -> None:
        def callback(name: str) -> None:
            self.gui.flowcharts[name] = Flowchart(name)
            self.gui.refresh_function_tabs()
        i = len(self.gui.flowcharts.values())
        new_name = f'fun_{i}'
        while new_name in self.gui.flowcharts.keys():
            i += 1
            new_name = f'fun_{i}'
        self.gui.modal_service.show_input_text_modal(
            'New Function',
            'Name',
            new_name,
            callback)
