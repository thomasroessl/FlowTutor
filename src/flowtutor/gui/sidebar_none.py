from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart
    from flowtutor.gui.gui import GUI
    from flowtutor.language_service import LanguageService
    from flowtutor.flowchart.node import Node


class SidebarNone(Sidebar):
    '''A GUI sidebar for no selected nodes.'''

    @inject
    def __init__(self, gui: GUI, language_service: LanguageService = Provide['language_service']) -> None:
        self.gui = gui
        self.language_service = language_service
        with dpg.group() as self.main_group:
            dpg.add_text('File head')
            with dpg.collapsing_header(label='Import') as self.import_header:
                pass
            with dpg.collapsing_header(label='Define') as self.define_header:
                with dpg.table(sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as self.table:

                    dpg.add_table_column()
                    dpg.add_table_column(width_fixed=True, width=12)

                    self.refresh_definitions(self.preprocessor_definitions())

                    with dpg.theme() as item_theme:
                        with dpg.theme_component(dpg.mvTable):
                            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1, category=dpg.mvThemeCat_Core)
                    dpg.bind_item_theme(self.table, item_theme)

                dpg.add_button(label='Add Definition',
                               callback=lambda: (self.preprocessor_definitions().append(''),
                                                 self.refresh_definitions(
                                   self.preprocessor_definitions()),
                                   gui.redraw_all(True)))
            with dpg.collapsing_header(label='Custom'):
                dpg.add_input_text(tag='selected_preprocessor_custom',
                                   width=-1,
                                   height=-46,
                                   multiline=True,
                                   callback=lambda _, data:
                                   (self.main_node().__setattr__('preprocessor_custom', data),
                                    gui.redraw_all(True)))
            dpg.add_spacer(height=3)
            dpg.add_separator()
            dpg.add_spacer(height=3)
            self.types_button = dpg.add_button(label='Types', width=-1,
                                               callback=lambda: (dpg.show_item('type_window'),
                                                                 gui.redraw_all(True)))

    def main_node(self) -> Flowchart:
        return self.gui.flowcharts['main']

    def imports(self) -> list[str]:
        result: list[str] = self.main_node().__getattribute__('imports')
        return result

    def preprocessor_definitions(self) -> list[str]:
        result: list[str] = self.main_node().__getattribute__('preprocessor_definitions')
        return result

    def on_header_checkbox_change(self, sender: Union[int, str], is_checked: bool) -> None:
        header = dpg.get_item_user_data(sender)
        if is_checked:
            self.imports().append(header)
        else:
            self.imports().remove(header)
        self.gui.redraw_all(True)

    def refresh_definitions(self, entries: list[str]) -> None:
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(self.table)[1]:
            dpg.delete_item(child)

        for i, entry in enumerate(entries):
            with dpg.table_row(parent=self.table):
                dpg.add_input_text(width=-1, height=-1, user_data=i,
                                   callback=lambda s, data: (self.preprocessor_definitions()
                                                             .__setitem__(dpg.get_item_user_data(s), data),
                                                             self.gui.redraw_all(True)),
                                   default_value=entry)

                delete_button = dpg.add_image_button('trash_image', user_data=i, callback=lambda s: (
                    self.preprocessor_definitions().pop(dpg.get_item_user_data(s)),
                    self.refresh_definitions(self.preprocessor_definitions()),
                    self.gui.redraw_all(True)
                ))
                with dpg.theme() as delete_button_theme:
                    with dpg.theme_component(dpg.mvImageButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 4, category=dpg.mvThemeCat_Core)

                dpg.bind_item_theme(delete_button, delete_button_theme)

    def refresh(self) -> None:
        if self.gui.selected_flowchart.lang_data['lang_id'] == 'c':
            dpg.show_item(self.types_button)
            dpg.show_item(self.define_header)
        else:
            dpg.hide_item(self.types_button)
            dpg.hide_item(self.define_header)
        if 'import' in self.gui.selected_flowchart.lang_data and\
           'standard_imports' in self.gui.selected_flowchart.lang_data:
            dpg.show_item(self.import_header)
        else:
            dpg.hide_item(self.import_header)
        self.refresh_definitions(self.preprocessor_definitions())
        dpg.configure_item(
            'selected_preprocessor_custom',
            default_value=self.main_node().__getattribute__('preprocessor_custom'))
        # delete existing entries to avoid duplicates
        for child in dpg.get_item_children(self.import_header)[1]:
            dpg.delete_item(child)
        for header in self.language_service.get_standard_headers(self.gui.selected_flowchart):
            dpg.add_checkbox(
                parent=self.import_header,
                label=header,
                default_value=header in self.imports(),
                user_data=header,
                callback=self.on_header_checkbox_change)
        for checkbox in dpg.get_item_children(self.import_header)[1]:
            dpg.configure_item(checkbox, default_value=dpg.get_item_user_data(checkbox) in self.imports())

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        self.gui.set_sidebar_title('Program')
        dpg.show_item(self.main_group)
