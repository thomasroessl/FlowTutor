from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.type_definition import TypeDefinition

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SectionTypedefs:
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.theme() as self.delete_button_theme:
            with dpg.theme_component(dpg.mvImageButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3, category=dpg.mvThemeCat_Core)
        self.main_header = dpg.add_collapsing_header(label='Type Definitions')
        self.refresh()

    def refresh(self) -> None:
        for child in dpg.get_item_children(self.main_header)[1]:
            dpg.delete_item(child)
        for [i, d] in enumerate(self.type_definitions()):
            if i > 0:
                dpg.add_spacer(height=5, parent=self.main_header)
            with dpg.group(horizontal=True, parent=self.main_header):
                dpg.add_text('Name')
                dpg.add_input_text(indent=50,
                                   width=-33,
                                   no_spaces=True,
                                   default_value=d.name,
                                   user_data=i,
                                   callback=lambda s, data: (
                                       self.type_definitions()[dpg.get_item_user_data(
                                           s)].__setattr__('name', data),
                                       self.gui.redraw_all()))
                delete_button = dpg.add_image_button(
                    'trash_image', height=18, width=18, user_data=i,
                    callback=lambda s: self.on_delete_definition(dpg.get_item_user_data(s)))
                dpg.bind_item_theme(delete_button, self.delete_button_theme)
            with dpg.group(horizontal=True, parent=self.main_header):
                dpg.add_text('Definition')
                dpg.add_input_text(indent=100,
                                   width=-1,
                                   default_value=d.name,
                                   user_data=i,
                                   callback=lambda s, data: (
                                       self.type_definitions()[dpg.get_item_user_data(
                                           s)].__setattr__('definition', data),
                                       self.gui.redraw_all()))

            dpg.add_spacer(height=5, parent=self.main_header)
            dpg.add_separator(parent=self.main_header)
        dpg.add_spacer(height=5, parent=self.main_header)
        dpg.add_button(label='Add Type Definition', parent=self.main_header, width=-1, callback=self.on_add_definition)

    def on_add_definition(self) -> None:
        self.type_definitions().append(TypeDefinition())
        self.refresh()
        self.gui.redraw_all()

    def on_delete_definition(self, index: int) -> None:
        del self.type_definitions()[index]
        self.refresh()
        self.gui.redraw_all()

    def main_node(self) -> Flowchart:
        return self.gui.flowcharts['main']

    def type_definitions(self) -> list[TypeDefinition]:
        return self.main_node().type_definitions
